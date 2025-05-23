import os
from math import isnan
from typing import Union

import time
import gspread
from gspread_dataframe import get_as_dataframe

from models.moduleBCSScore.module import BCSScoreModule
from models.moduleBreedGrade.module import BreedGradeModule
from models.moduleBreedPred.module import BreedPredModule
from models.moduleCleftStatus.module import CleftStatusModule
from models.moduleDiarrheaPred.module import DiarrheaPredModule
from models.moduleFMDPred.module import FMDPredModule
from models.moduleFleabitePred.module import FleabitePredModule
from models.moduleHornPred.module import HornPredModule
from models.moduleLSDPred.module import LSDPredModule
from models.moduleMastitisPred.module import MastitisPredModule
from models.moduleRumination.module import RuminationModule
from models.moduleSFRQA.module import SFRQAModule
from models.moduleSFRQAv2_5.module import SFRQAv2_5Module
from models.moduleSFRQAv3.module import SFRQAv3Module
from models.moduleScrotumPred.module import ScrotumPredModule
from models.moduleSkinCoatPred.module import SkinCoatPredModule
from models.moduleTeatScore.module import TeatScoreModule
from models.moduleUdderPred.module import UdderPredModule
from models.moduleWormPred.module import WormPredModule
from models.moduleWoundStatus.module import WoundStatusModule

# gc = gspread.service_account(filename="secrets/sheets.env.json")
#
# spreadsheet = gc.open("RulesDB")
#
# languages = {"en": "English", "hi": "Hindi", "kn": "Kannada"}
# cattle_feedback = get_as_dataframe(spreadsheet.worksheet("cattle_feedback"))
# disease_feedback = get_as_dataframe(spreadsheet.worksheet("disease_feedback"))
# buying_rules = get_as_dataframe(spreadsheet.worksheet("buying_recommendation_rules"))
# buying_rules = dict(zip(buying_rules["Label"], buying_rules["Buying Recommendations"]))
#
# breeding_capacity_rules = get_as_dataframe(spreadsheet.worksheet("Breeding_Capacity"))
# breeding_capacity_rules = dict(
#     zip(breeding_capacity_rules["Label"], breeding_capacity_rules["Breeding Capacity"])
# )
#
# milk_yield_df = get_as_dataframe(spreadsheet.worksheet("milk_yield_data"))
#
# mul_factors_green_dry = get_as_dataframe(spreadsheet.worksheet("multiply_factor_green&dry"))
# mul_factors_maize_silage = get_as_dataframe(spreadsheet.worksheet("multiply_factor"))
# div_factors = get_as_dataframe(spreadsheet.worksheet("div_factor"))

_sheet_data = {}
_last_refresh_time = 0
REFRESH_INTERVAL = 24*60*60


def refresh_sheet_data():
    global _sheet_data, _last_refresh_time

    current_time = time.time()
    if current_time - _last_refresh_time < REFRESH_INTERVAL:
        return

    auth_token_path = os.path.abspath(
        os.path.dirname(__file__) + "/../secrets/sheets.env.json"
    )
    gc = gspread.service_account(filename=auth_token_path)
    spreadsheet = gc.open("RulesDB")

    _sheet_data = {
        "cattle_feedback": get_as_dataframe(spreadsheet.worksheet("cattle_feedback")),
        "disease_feedback": get_as_dataframe(spreadsheet.worksheet("disease_feedback")),
        "buying_rules": get_as_dataframe(
            spreadsheet.worksheet("buying_recommendation_rules")
        ),
        "breeding_capacity_rules": get_as_dataframe(
            spreadsheet.worksheet("Breeding_Capacity")
        ),
        "milk_yield_df": get_as_dataframe(spreadsheet.worksheet("milk_yield_data")),
        "mul_factors_green_dry": get_as_dataframe(
            spreadsheet.worksheet("multiply_factor_green&dry")
        ),
        "mul_factors_maize_silage": get_as_dataframe(
            spreadsheet.worksheet("multiply_factor")
        ),
        "div_factors": get_as_dataframe(spreadsheet.worksheet("div_factor")),
    }

    _last_refresh_time = current_time


def get_sheet_data(sheet_name):
    refresh_sheet_data()
    return _sheet_data[sheet_name]


languages = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada",
    "ml": "Malayalam",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati"
}

default_messages = {
    "English": ("No specific recommendation", "No specific interpretation"),
    "Hindi": ("कोई विशेष निर्देश नहीं", "कोई विशेष व्याख्या नहीं"),
    "Kannada": ("ನಿರ್ದಿಷ್ಟ ಶಿಫಾರಸು ಇಲ್ಲ", "ನಿರ್ದಿಷ್ಟ ವ್ಯಾಖ್ಯಾನ ಇಲ್ಲ"),
    "Malayalam": ("പ്രത്യേക ശുപാർശ ഇല്ലm", "പ്രത്യേക വ്യാഖ്യാനമില്ല"),
    "Tamil": ("குறிப்பிட்ட பரிந்துரை இல்லை", "குறிப்பிட்ட வியாகனம் இல்லை"),
    "Telugu": ("ప్రత్యేక సహాయాలు ఇల్లు", "ప్రత్యేక వ్యాఖ్యానము ఇల్లు"),
    "Marathi": ("कोणतीही विशिष्ट शिफारस नाही","विशिष्ट व्याख्या नाही"),
    "Gujarati": ("કોઈ ચોક્કસ ભલામણ નથી", "કોઈ ચોક્કસ અર્થઘટન નથી")
}

feed_name_codes = {
    "mzs": "maize-silage",
    "gmf": "green-maize-fodder",
    "rgs": "rs-ws-ps",
    "gfs": "green-fodder",
    "csc": "cotton-seed-cake",
    "mcd": "maize-cracked",
    "gdc": "grnd-nut-cake",
    "cf18": "cmg-18",
    "cf22": "cmg-22",
    "drf": "dairy-fortune",
}


def get_language_and_defaults(language_code: str):
    """Fetch the language and default messages."""
    language = languages.get(language_code, "English")
    return language, default_messages.get(language, default_messages["English"])


def get_feedback(column_name, predicted_value, language_code: str = "en"):
    language, (rec, interp) = get_language_and_defaults(language_code)
    cattle_feedback = get_sheet_data("cattle_feedback")
    hit = cattle_feedback[cattle_feedback[column_name] == predicted_value]
    if not hit.empty:
        rec = hit[f"Recommendation({language})"].values[0]
        interp = hit[f"Interpretations({language})"].values[0]
        if isinstance(rec, float) and isnan(rec):
            rec = default_messages[language][0]
        if isinstance(interp, float) and isnan(interp):
            interp = default_messages[language][1]
    return {
        "recommendation": rec,
        "interpretation": interp,
    }


def get_disease_feedback(disorder_type, predicted_value, language_code):
    language, (rec, interp) = get_language_and_defaults(language_code)
    disease_feedback = get_sheet_data("disease_feedback")
    hit = disease_feedback[
        (disease_feedback["Type"] == disorder_type)
        & (
            disease_feedback["Present"]
            == ("No" if predicted_value == "healthy" else "Yes")
        )
    ]
    if not hit.empty:
        rec = hit[f"RECOMMENDATION({language})"].values[0]
        interp = hit[f"INTERPRETATION({language})"].values[0]
        if isinstance(rec, float) and isnan(rec):
            rec = default_messages[language][0]
        if isinstance(interp, float) and isnan(interp):
            interp = default_messages[language][1]
    return {
        "recommendation": rec,
        "interpretation": interp,
    }


def get_buying_recommendations(
    predicted_skincoat, predicted_wormload, predicted_bcs, predicted_uddertype
):
    buying_rules = get_sheet_data("buying_rules")
    buying_rules = dict(
        zip(buying_rules["Label"], buying_rules["Buying Recommendations"])
    )
    if predicted_uddertype == "Null":
        return "Null"
    else:
        recommendations = [
            buying_rules.get(predicted_skincoat),
            buying_rules.get(predicted_wormload),
            buying_rules.get(predicted_uddertype),
            buying_rules.get(f"BCS-{predicted_bcs}"),
        ]
        recommendations = [rec for rec in recommendations if rec is not None]

        no_cnt = recommendations.count("No")
        yes_cnt = recommendations.count("Yes")
        chk_cnt = recommendations.count("Physical Check required")

        if no_cnt >= 2:
            return "No"
        if yes_cnt >= 2:
            return "Yes"
        return "Physical Check required" if chk_cnt > 0 else "Physical Check required"


def get_breeding_capacity(
    predicted_skincoat, predicted_wormload, predicted_bcs, predicted_uddertype
):
    breeding_capacity_rules = get_sheet_data("breeding_capacity_rules")
    breeding_capacity_rules = dict(
        zip(
            breeding_capacity_rules["Label"],
            breeding_capacity_rules["Breeding Capacity"],
        )
    )
    if predicted_uddertype == "Null":
        return "Null"
    else:
        capacities = [
            breeding_capacity_rules.get(predicted_skincoat),
            breeding_capacity_rules.get(predicted_wormload),
            breeding_capacity_rules.get(f"BCS-{predicted_bcs}"),
        ]

        good_count = capacities.count("Good")
        poor_count = capacities.count("Poor")

        if good_count == 3:
            return "Good"
        elif poor_count == 3:
            return "Poor"
        else:
            return "Fair"


def get_animal_alertness(rumination_category):
    rumination_alertness_pairs = {"Good": "Active", "Fair": "Dull", "Poor": "Depressed"}

    return rumination_alertness_pairs.get(
        rumination_category, "Could not determine animal alertness"
    )


def get_production_capacity(breed, breed_grade, bcs_value, udder_type):
    milk_yield_df = get_sheet_data("milk_yield_df")
    if udder_type == "Null":
        return "Null"
    else:
        mask = (
            (milk_yield_df["Breed"] == breed)
            & (milk_yield_df["Breed Grade"] == breed_grade)
            & (milk_yield_df["BCS Min"] <= bcs_value)
            & (milk_yield_df["BCS Max"] >= bcs_value)
        )
        return (
            milk_yield_df.loc[mask, "Production Capacity range"].values[0]
            if mask.any()
            else "Null"
        )


def get_range_values(breed, breed_grade, bcs_value, udder_type):
    milk_yield_df = get_sheet_data("milk_yield_df")
    if udder_type == "Null":
        return "Null", "Null", "Null"
    else:
        if all(v is not None and v != "Null" for v in [breed, breed_grade, bcs_value]):
            bcs_value = (
                float(bcs_value.split("-")[-1])
                if isinstance(bcs_value, str)
                else bcs_value
            )
            mask = (
                (milk_yield_df["Breed"] == breed)
                & (milk_yield_df["Breed Grade"] == breed_grade)
                & (milk_yield_df["BCS Min"] <= bcs_value)
                & (milk_yield_df["BCS Max"] >= bcs_value)
            )

            if mask.any():
                milk_yield_range = milk_yield_df.loc[mask, "Milk Yield range"].values[0]
                market_value_range = milk_yield_df.loc[
                    mask, "Market Value range"
                ].values[0]
                lactation_yield_range = milk_yield_df.loc[
                    mask, "Lactation Yield range"
                ].values[0]
                return milk_yield_range, market_value_range, lactation_yield_range
        return "Null", "Null", "Null"


def get_weight(
    bcs_label: float = 3, breed_label: str = "Cow-Jersey-Crossbreed"
) -> Union[float, str]:
    if breed_label == "Cow-ND":
        breed_label = "Cow-Non-Descript-Breed"
    breed_weights = {
        "Buffalo-Banni": 550,
        "Buffalo-Bhadavari": 500,
        "Buffalo-Jafarabadi": 800,
        "Buffalo-Mehasana": 500,
        "Buffalo-Murha": 600,
        "Buffalo-ND": 450,
        "Buffalo-Nili-Ravi": 550,
        "Buffalo-Pandarapuri": 450,
        "Buffalo-Surti": 425,
        "Buffalo-Toda": 350,
        "Cow-Amrutmahal": 350,
        "Cow-Deoni": 450,
        "Cow-Gir": 450,
        "Cow-HF-Crossbreed": 525,
        "Cow-Hallikar": 350,
        "Cow-Jersey-Crossbreed": 450,
        "Cow-Kankrej": 450,
        "Cow-Malanad-Gidda": 160,
        "Cow-Non-Descript-Breed": 400,
        "Cow-Red-Sindhi": 450,
        "Cow-Sahiwal": 462.5,
    }

    bcs_adjustments = {
        1: -0.20,
        1.25: -0.18,
        1.5: -0.15,
        1.75: -0.12,
        2: -0.10,
        2.25: -0.07,
        2.5: -0.05,
        2.75: -0.02,
        3: 0.00,
        3.25: 0.02,
        3.5: 0.05,
        3.75: 0.07,
        4: 0.10,
        4.25: 0.12,
        4.5: 0.15,
        4.75: 0.18,
        5: 0.20,
    }

    base_weight = breed_weights.get(breed_label, None)
    if base_weight is None:
        return "Could not determine"

    bcs_factor = bcs_adjustments.get(bcs_label, None)
    if bcs_factor is None:
        return "Could not determine"

    weight = base_weight + (base_weight * bcs_factor)
    return weight


def get_nutrition_values(
    weight: int, production_capacity_range: str, fodder_type: str = "green_dry"
):
    mul_factors_green_dry = get_sheet_data("mul_factors_green_dry")
    mul_factors_maize_silage = get_sheet_data("mul_factors_maize_silage")
    div_factors = get_sheet_data("div_factors")
    mul_factors_df = (
        mul_factors_green_dry
        if fodder_type == "green_dry"
        else mul_factors_maize_silage
    )
    if production_capacity_range in (None, "0", "Null"):
        return {feed_name_codes[code]: None for code in mul_factors_df["feed_name"]}

    production_capacity_lower, production_capacity_upper = map(
        float, production_capacity_range.split("-")
    )
    avg_production_capacity = (
        production_capacity_lower + production_capacity_upper
    ) / 2
    dmd = weight * 0.03

    production_capacity_col = None
    for col in mul_factors_df.columns:
        if "-" in col:
            lower_bound, upper_bound = map(float, col.split("-"))
            if lower_bound <= avg_production_capacity < upper_bound:
                production_capacity_col = col
                break
    if production_capacity_col is None:
        production_capacity_col = mul_factors_df.columns[-1]

    recommendations = (mul_factors_df[production_capacity_col] * dmd) / div_factors[
        "div_factor"
    ]
    rounded_recommendations = (
        recommendations.round(2)
        if production_capacity_col == "drf"
        else recommendations.round(1)
    )
    out = {
        feed_name_codes[code]: value
        for code, value in zip(mul_factors_df["feed_name"], rounded_recommendations)
    }
    out["dairy-fortune"] = out["dairy-fortune"] * 1000
    return out
