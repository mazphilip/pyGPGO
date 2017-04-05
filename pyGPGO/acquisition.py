import numpy as np
from scipy.stats import norm


class Acquisition:
    def __init__(self, mode, eps=1e-06, **params):
        """
        Acquisition function class.

        Parameters
        ----------
        mode: str
            Either `ExpectedImprovement`, `ProbabilityImprovement` or `UCB`. Defines the
            behaviour of the acquisition strategy.
        eps: float
            Small floating value to avoid `np.sqrt` or zero-division warnings.
        params: float
            Extra parameters needed for certain acquisition functions, e.g. UCB needs
            to be supplied with `beta`.
        """
        self.params = params
        self.eps = eps
        if mode == 'ExpectedImprovement':
            self.f = self.ExpectedImprovement
        elif mode == 'IntegratedExpectedImprovement':
            self.f = self.IntegratedExpectedImprovement
        elif mode == 'ProbabilityImprovement':
            self.f = self.ProbabilityImprovement
        elif mode == 'UCB':
            self.f = self.UCB
        elif mode == 'Entropy':
            self.f = self.Entropy
        else:
            raise NotImplementedError('Not recognised acquisition function')

    def ProbabilityImprovement(self, tau, mean, std):
        """
        Probability of Improvement acquisition function.

        Parameters
        ----------
        tau: float
            Best observed function evaluation.
        mean: float
            Point mean of the posterior process.
        std: float
            Point std of the posterior process.

        Returns
        -------
        float
            Probability of improvement.
        """
        z = (mean - tau - self.eps) / (std + self.eps)
        return norm.cdf(z)

    def ExpectedImprovement(self, tau, mean, std):
        """
        Expected Improvement acquisition function.

        Parameters
        ----------
        tau: float
            Best observed function evaluation.
        mean: float
            Point mean of the posterior process.
        std: float
            Point std of the posterior process.

        Returns
        -------
        float
            Expected improvement.
        """
        z = (mean - tau - self.eps) / (std + self.eps)
        return (mean - tau) * norm.cdf(z) + std * norm.pdf(z)[0]

    def UCB(self, tau, mean, std, beta):
        """
        Upper-confidence bound acquisition function.

        Parameters
        ----------
        tau: float
            Best observed function evaluation.
        mean: float
            Point mean of the posterior process.
        std: float
            Point std of the posterior process.
        beta: float
            Hyperparameter controlling exploitation/exploration ratio.

        Returns
        -------
        float
            Upper confidence bound.
        """
        return mean + beta * std

    def Entropy(self, tau, mean, std, sigman):
        """
        Predictive entropy acquisition function

        Parameters
        ----------
        tau: float
            Best observed function evaluation.
        mean: float
            Point mean of the posterior process.
        std: float
            Point std of the posterior process.
        sigman: float
            Noise variance

        Returns
        -------
        float:
            Predictive entropy.
        """
        sp2 = std **2 + sigman
        return 0.5 * np.log(2 * np.pi * np.e * sp2)

    def IntegratedExpectedImprovement(self, tau, meanmcmc, stdmcmc):
        """
        Integrated expected improvement. Can only be used with `GaussianProcessMCMC` instance.
        
        Parameters
        ----------
        tau: float
            Best observed function evaluation
        meanmcmc: array-like
            Means of posterior predictive distributions after sampling.
        stdmcmc
            Standard deviations of posterior predictive distributions after sampling.
            
        Returns
        -------
        float:
            Integrated Expected Improvement
        """
        acq = [self.ExpectedImprovement(tau, np.array([mean]), np.array([std])) for mean, std in zip(meanmcmc, stdmcmc)]
        return np.average(acq)

    def IntegratedProbabilityImprovement(self, tau, meanmcmc, stdmcmc):
        """
        Integrated probability of improvement. Can only be used with `GaussianProcessMCMC` instance.

        Parameters
        ----------
        tau: float
            Best observed function evaluation
        meanmcmc: array-like
            Means of posterior predictive distributions after sampling.
        stdmcmc
            Standard deviations of posterior predictive distributions after sampling.

        Returns
        -------
        float:
            Integrated Probability of Improvement
        """
        acq = [self.ProbabilityImprovement(tau, np.array([mean]), np.array([std])) for mean, std in zip(meanmcmc, stdmcmc)]
        return np.average(acq)

    def IntegratedUCB(self, tau, meanmcmc, stdmcmc, beta):
        """
        Integrated probability of improvement. Can only be used with `GaussianProcessMCMC` instance.

        Parameters
        ----------
        tau: float
            Best observed function evaluation
        meanmcmc: array-like
            Means of posterior predictive distributions after sampling.
        stdmcmc
            Standard deviations of posterior predictive distributions after sampling.
            
        beta: float
            Hyperparameter controlling exploitation/exploration ratio.
            
        Returns
        -------
        float:
            Integrated UCB.
        """
        acq = [self.UCB(tau, np.array([mean]), np.array([std]), beta) for mean, std in zip(meanmcmc, stdmcmc)]
        return np.average(acq)

    def eval(self, tau, mean, std):
        """
        Evaluates selected acquisition function.

        Parameters
        ----------
        tau: float
            Best observed function evaluation.
        mean: float
            Point mean of the posterior process.
        std: float
            Point std of the posterior process.

        Returns
        -------
        float
            Acquisition function value.

        """
        return self.f(tau, mean, std, **self.params)
