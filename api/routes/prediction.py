from fastapi import APIRouter, Depends

from api.auth import verify_api_key
from api.models.prediction import SalesPrediction
from ml.prediction.predict_sales import (
    FEATURE_FILE,
    load_model,
    create_predictions,
)

router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"],
    dependencies=[Depends(verify_api_key)],
)


@router.get(
    "/sales",
    response_model=list[SalesPrediction],
)
def sales_predictions():
    import pandas as pd

    df = pd.read_csv(FEATURE_FILE)
    model = load_model()

    predictions = create_predictions(
        model,
        df,
    )

    return predictions.to_dict(orient="records")