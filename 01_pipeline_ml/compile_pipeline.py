from kfp import compiler
from pipelines.churn_pipeline import main_pipeline
import traceback

def traceback_error(error_obj, only_last=False):
    """
    Retorna el traceback formateado y el mensaje de error como string.
    """
    tb = traceback.format_exc()
    msg = str(error_obj)
    if only_last:
        tb = tb.strip().split('\n')[-1]
    return tb, msg

if __name__ == "__main__":
    try:
        compiler.Compiler().compile(
            pipeline_func=main_pipeline,
            package_path="compiled/churn_pipeline.yaml"
        )

        print("")
        print(f"-------------------")
        print(f"# COMPILE SUCCEED #")        
        print(f"-------------------")
        print("✅ Pipeline compilado en: compiled/churn_pipeline.yaml\n")

    except Exception as e:
        print("")
        print(f"-----------------")
        print(f"# COMPILE ERROR #")
        print(f"-----------------")
        tb, msg = traceback_error(e)
        print(tb)
        print(f"\\n❌ {msg}")