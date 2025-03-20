
from group import Group
from preprocessing.src.models.types.measurement_type import MeasurementType

folder = '../../../csv-data/input/sample_group/'
output = '../../../csv-data/output/sample_group/'

group = Group('example group', folder, output_folder=output)

group.aggregate([MeasurementType.CPU_ENERGY])

# group.summarize()

group.print()
print(group.aggregate_data.columns)
