SEED = 42
USECOLS = ["BusinessYear", "StateCode", "IssuerId", "PlanId", "RatingAreaId", "Tobacco", "Age",
           "IndividualRate", "IndividualTobaccoRate"]
TARGET = "IndividualRate"
CAT_FEATURES = ["StateCode", "IssuerId", "RatingAreaId", "Tobacco"]
NUM_FEATURES = ["BusinessYear", "age_num", "family_option"]
FEATURES = CAT_FEATURES + NUM_FEATURES
# Never used as features for the rate: the target itself, and the tobacco-user price,
# which is a surcharge on top of the same rate (a near copy of the target).
FORBIDDEN = ["IndividualRate", "IndividualTobaccoRate", "RateCategory"]
CLASSES = ["Low", "Medium", "High"]
