import unittest
import numpy as np
from gamma_probe import phase_surrogate, gamma_hat
import alive_reward_demo as A
from scale_capacity import probe_alive


class RepairTests(unittest.TestCase):
    def test_multivariate_phase_preserves_full_cross_spectrum(self):
        for n in (255,256):
            rng=np.random.default_rng(81); y=rng.normal(size=(n,3))+[-2,3,1]
            x=phase_surrogate(y,np.random.default_rng(19))
            f=np.fft.rfft(y,axis=0);g=np.fft.rfft(x,axis=0)
            np.testing.assert_allclose(x.mean(0),y.mean(0),atol=1e-12)
            np.testing.assert_allclose(g[:,:,None]*g[:,None,:].conj(),f[:,:,None]*f[:,None,:].conj(),atol=1e-8)
            self.assertFalse(np.allclose(x,y))

    def test_null_name_cannot_silently_fall_back(self):
        with self.assertRaises(ValueError):gamma_hat(np.ones((30,2)),null='phsae')

    def test_nonzero_capacity_start_and_explicit_zero_control(self):
        self.assertEqual(probe_alive(16,1.5,18,initial_rms=0),1/300)
        self.assertGreater(probe_alive(16,1.5,18),1/300)

    def test_capped_spread_gradient_finite_difference(self):
        x=np.random.default_rng(4).normal(scale=.12,size=(7,3))
        analytic=A.dcapspread(x,R=.5)
        def objective(z):
            i,j=np.triu_indices(len(z),1)
            return np.minimum(np.linalg.norm(z[i]-z[j],axis=1),.5).mean()
        for i in range(7):
            for j in range(3):
                a=x.copy();b=x.copy();a[i,j]+=1e-6;b[i,j]-=1e-6
                self.assertAlmostEqual(analytic[i,j],(objective(a)-objective(b))/2e-6,places=6)

    def test_toy_two_updates_match_independent_torch_autograd(self):
        import torch
        old=(A.H,A.T,A.EPOCHS)
        try:
            A.H,A.T,A.EPOCHS=3,9,2
            seed=17;lam=.03;rng=np.random.default_rng(seed)
            w=rng.standard_normal((3,3));w=w*(.4/max(abs(np.linalg.eigvals(w))))
            values={'W_h':w,'W_x':rng.standard_normal(3)*.5,'b':np.zeros(3),
                    'Wy':rng.standard_normal(3)*.1,'z':np.zeros(3)}
            p={k:torch.tensor(v,dtype=torch.float64,requires_grad=True) for k,v in values.items()}
            opt=torch.optim.Adam(list(p.values()),lr=A.LR,eps=1e-8,foreach=False)
            xs=torch.tensor(A.task_series(9,seed=seed),dtype=torch.float64)
            for _ in range(2):
                g=p['z'].sigmoid();h=torch.zeros(3,dtype=torch.float64);hf=h.clone();ys=[];states=[]
                for x in xs:
                    h=torch.tanh(p['W_h']@(h*g)+p['W_x']*x+p['b']);ys.append(p['Wy']@(h*g))
                    hf=torch.tanh(p['W_h']@(hf*g)+p['b']);states.append(hf)
                loss=(torch.stack(ys)-xs).square().mean()-lam*torch.pdist(torch.stack(states)).clamp(max=np.sqrt(3/16)).mean()+A.MU*g.mean()
                opt.zero_grad();loss.backward()
                for v in p.values():v.grad.clamp_(-5,5)
                opt.step()
            actual,_,_=A.train(seed,lam,mode='cap')
            for k in p:np.testing.assert_allclose(actual[k],p[k].detach().numpy(),rtol=1e-8,atol=1e-9)
        finally:A.H,A.T,A.EPOCHS=old


if __name__=='__main__':unittest.main()
