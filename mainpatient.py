from BetaTestAnalysisCode.PatientBetaTestAnalysis import PatientBetaTestAnalysis

database = ("localhost", 'root', 'moxie100')
tester = PatientBetaTestAnalysis(database, day=4)
tester.start()
tester.join()
