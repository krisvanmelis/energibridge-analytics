"""
Debug tool to inspect MeasurementType enum values
Run this script to print out all enum values and verify they're correct.
"""
import sys
import logging

from models.types.measurement_type import MeasurementType

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def inspect_enum():
    """Inspect and print all enum values"""
    logger.info("Inspecting MeasurementType enum")
    
    try:
        logger.info("All MeasurementType enum values:")
        for mt in MeasurementType:
            logger.info(f"  - {mt.name} = {mt.value} ({type(mt.value)}) -> column: {mt.column_name}")
        
        logger.info("\nTesting value lookups:")
        for value in [0, 1, 10, 20, 21, 30, 50, 80]:
            try:
                mt = MeasurementType(value)
                logger.info(f"  MeasurementType({value}) -> {mt.name}")
            except ValueError as e:
                logger.error(f"  MeasurementType({value}) -> ERROR: {e}")
        
    except Exception as e:
        logger.error(f"Error inspecting enum: {e}", exc_info=True)
        return False
        
    return True

if __name__ == "__main__":
    success = inspect_enum()
    sys.exit(0 if success else 1)
