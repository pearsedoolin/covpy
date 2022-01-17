import covpy
import matplotlib.pyplot as plt

dataCollector = covpy.DataCollector()

cases = dataCollector.get_covid19_cases()
countries = ['Canada', 'France', 'Spain']
ax = cases[countries].plot()
ax.set_ylabel("Confirmed Covid19 Cases")
plt.show()