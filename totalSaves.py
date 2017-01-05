from BetaTestAnalysisCode.PatientBetaTestAnalysis import PatientBetaTestAnalysis

database = ("localhost", 'root', 'moxie100')
for day in range (1, 157):
    tester = PatientBetaTestAnalysis(database, day=day)
    tester.start()
    tester.join()
