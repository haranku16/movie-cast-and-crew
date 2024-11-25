from statsmodels.stats.power import TTestIndPower

def main():
    '''
    Entrypoint function for the power analysis script.
    '''

    # Initialize the power analysis
    analysis = TTestIndPower()
    # Bonferroni correction
    inputs = { 'all', 'actor', 'actress', 'director', 'writer', 'producer', 'cinematographer', 'composer', 'editor', 'production designer' }
    outputs = {'average rating'}
    num_hypotheses = len(inputs) * len(outputs)
    alpha = 0.05/num_hypotheses
    # Calculate the sample size needed
    result = analysis.solve_power(effect_size=0.2, alpha=alpha,
    power=0.8, ratio=1.0, alternative='two-sided')
    print(f'Sample size needed: {result:.0f}')

if __name__ == '__main__':
    main()
