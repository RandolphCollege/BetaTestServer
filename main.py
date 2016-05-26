from BetaTestAnalysisCode.RunBetaTestAnalysis import RunBetaTestAnalysis

database = ("localhost", 'root', 'moxie100')
tester = RunBetaTestAnalysis(database)
tester.start()
tester.join()
