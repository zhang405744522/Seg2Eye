import numpy as np
import torch
import torch.nn.functional as F


class ExpertsAngularError(object):

    _to_degrees = 180. / np.pi

    def pred_to_vector(self, a):
        if a.shape[2] == 2:
            sin = torch.sin(a)
            cos = torch.cos(a)
            v = torch.stack([
                cos[:, :, 0] * sin[:, :, 1],
                -sin[:, :, 0],
                cos[:, :, 0] * cos[:, :, 1],
            ], dim=2)
        elif a.shape[2] == 3:
            v = F.normalize(a)
        else:
            raise ValueError('Do not know how to convert tensor of size %s' % a.shape)
        return v

    def true_to_vector(self, a):
        assert a.shape[1] == 2
        sin = torch.sin(a)
        cos = torch.cos(a)
        v = torch.stack([
            cos[:, 0] * sin[:, 1],
            -sin[:, 0],
            cos[:, 0] * cos[:, 1],
        ], dim=1)
        v = torch.unsqueeze(v, 1)  # Get ready for sim against expert preds
        return v

    def __call__(self, g_pred_experts, g_true):
        g_pred_experts = self.pred_to_vector(g_pred_experts)
        g_true = self.true_to_vector(g_true)
        sim = F.cosine_similarity(g_pred_experts, g_true, dim=2, eps=1e-8)
        sim = F.hardtanh_(sim, min_val=-1+1e-8, max_val=1-1e-8)
        return torch.acos(sim) * self._to_degrees
