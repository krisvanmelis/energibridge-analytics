import models.trial as trial
import dashboards as dashboards
from models.types.measurement_type import MeasurementType

filepath = "../../csv-data/output/group1/large_specific_extensions_0_preprocessed.csv"

t = trial.Trial(preprocessed_path=filepath)

print(t.no_cores())
print(t.no_logical())

mt = [MeasurementType.POWER_PER_CORE]

columns = []

intermediate = [dashboards.measurement_type_to_columns(
                            measurement_type,
                            t.no_cores(),
                            t.no_logical())
                         for measurement_type in mt]
columns = columns + [c for c in intermediate]

print(intermediate)

t2 = dashboards. measurement_type_to_columns(MeasurementType.POWER_PER_CORE, t.no_cores(), t.no_logical())

print(columns)