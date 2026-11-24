from flask import Flask, render_template, session, redirect, url_for, request
import json
from pymongo import MongoClient, ReturnDocument
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from config import MONGO_URI
import joblib
from flask import flash
from uuid import uuid4
import os

# ============================================================
# APP CONFIGURATION
# ============================================================



app = Flask(__name__)
app.secret_key = os.getenv(
    "SECRET_KEY",
    "temporary-development-secret-change-before-deployment"
)


# ============================================================
# SUPPORTED LANGUAGES
# ============================================================

SUPPORTED_LANGUAGES = {
    "en": "English",
    "pa": "ਪੰਜਾਬੀ",
    "hi": "हिन्दी"
}


@app.context_processor
def inject_language():
    return {
        "current_language": session.get("language", "en"),
        "supported_languages": SUPPORTED_LANGUAGES
    }


@app.route("/set-language/<language>")
def set_language(language):

    if language in SUPPORTED_LANGUAGES:
        session["language"] = language

    return redirect(
        request.referrer
        or url_for("home")
    )


# ============================================================
# TRANSLATION LOADER
# ============================================================
def load_translations(language):

    if language not in SUPPORTED_LANGUAGES:
        language = "en"

    file_path = os.path.join(
        app.root_path,
        "translations",
        f"{language}.json"
    )

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):
        return {}

@app.context_processor
def inject_translations():

    language = session.get("language", "en")
    translations = load_translations(language)

    app.logger.info(
        "Selected language: %s | Translation keys loaded: %s",
        language,
        len(translations)
    )

    return {
        "translations": translations
    }
# ============================================================
# MONGODB CONNECTION
# ============================================================

client = MongoClient(MONGO_URI)

db = client["AgroReForm"]


# ============================================================
# COLLECTIONS
# ============================================================

farmers_collection = db["farmers"]

farms_collection = db["farms"]

crop_records_collection = db["crop_records"]

input_records_collection = db["input_records"]

analysis_results_collection = db["analysis_results"]

awareness_records_collection = db["awareness_records"]

counters_collection = db["counters"]

crop_problem_reports_collection = db["crop_problem_reports"]
# ============================================================
# MACHINE LEARNING MODEL
# ============================================================

model_package = joblib.load(
    "agroreform_model_package.pkl"
)

ml_model = model_package["model"]

ml_features = model_package["features"]


# ============================================================
# GENERATE FARMER ID
# ============================================================
def generate_farmer_id():
    max_existing_number = 0

    existing_farmers = farmers_collection.find(
        {},
        {"farmer_id": 1}
    )

    for farmer in existing_farmers:
        farmer_id = farmer.get("farmer_id", "")

        if isinstance(farmer_id, str) and farmer_id.startswith("ARF"):
            number_part = farmer_id[3:]

            if number_part.isdigit():
                number = int(number_part)
                max_existing_number = max(
                    max_existing_number,
                    number
                )

    counters_collection.update_one(
        {"_id": "farmer_id"},
        {
            "$max": {
                "sequence": max_existing_number
            }
        },
        upsert=True
    )

    counter = counters_collection.find_one_and_update(
        {"_id": "farmer_id"},
        {
            "$inc": {
                "sequence": 1
            }
        },
        return_document=ReturnDocument.AFTER
    )

    next_number = counter["sequence"]
    farmer_id = f"ARF{next_number:06d}"

    return farmer_id, next_number
# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template(
        "home.html"
    )


# ============================================================
# FARMER REGISTRATION
# ============================================================

@app.route(
    "/farmer",
    methods=["GET", "POST"]
)
def farmer():
    if request.method == "POST":

        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if len(password) < 8:
            return "Password must contain at least 8 characters.", 400

        if password != confirm_password:
            return "Passwords do not match. Please try again.", 400

        password_hash = generate_password_hash(password)

        # Continue with your existing registration code below


        # ----------------------------------------------------
        # GENERATE IDENTIFIERS
        # ----------------------------------------------------

        farmer_id, farmer_id_number = (
            generate_farmer_id()
        )

        farm_id = (
            f"{farmer_id}-F1"
        )

        record_id = (
            f"{farmer_id}-R1"
        )

        input_id = (
            f"{farmer_id}-R1-I1"
        
        )
        


        # ----------------------------------------------------
        # FARMER PROFILE
        #
        # IMPORTANT:
        # farmer.html uses name="block"
        # ----------------------------------------------------

        farmer_document = {

    "farmer_id":
        farmer_id,

    "farmer_id_number": farmer_id_number,

    "password_hash":
        password_hash,

            "district":
                request.form.get(
                    "district",
                    ""
                ),

            "block_tehsil":
                request.form.get(
                    "block",
                    ""
                ),

            "village":
                request.form.get(
                    "village",
                    ""
                ),

            "land_ownership":
                request.form.get(
                    "land_ownership",
                    ""
                )
        }


        # ----------------------------------------------------
        # FARM DATA
        # ----------------------------------------------------

        farm_document = {

            "farmer_id":
                farmer_id,

            "farm_id":
                farm_id,

            "farm_area":
                request.form.get(
                    "farm_area",
                    ""
                ),

            "area_unit":
                request.form.get(
                    "area_unit",
                    ""
                )
        }


        # ----------------------------------------------------
        # CROP DATA
        # ----------------------------------------------------

        crop_document = {

            "farmer_id":
                farmer_id,

            "farm_id":
                farm_id,

            "record_id":
                record_id,

            "crop":
                request.form.get(
                    "crop",
                    ""
                ),

            "cotton_variety":
                request.form.get(
                    "cotton_variety",
                    ""
                ),

            "farming_year":
                request.form.get(
                    "farming_year",
                    ""
                ),

            "previous_crop":
                request.form.get(
                    "previous_crop",
                    ""
                ),

            "farm_area":
                request.form.get(
                    "farm_area",
                    ""
                ),

            "cotton_area":
                request.form.get(
                    "cotton_area",
                    ""
                ),

            "production":
                request.form.get(
                    "production",
                    ""
                ),

            "production_unit":
                request.form.get(
                    "production_unit",
                    ""
                ),

            "selling_price":
                request.form.get(
                    "selling_price",
                    ""
                ),

            "major_problem":
                request.form.get(
                    "major_problem",
                    ""
                ),

            "irrigation_type":
                request.form.get(
                    "irrigation_type",
                    ""
                ),

            "number_of_irrigations":
                request.form.get(
                    "number_of_irrigations",
                    ""
                )
        }


        # ----------------------------------------------------
        # INPUT / COST DATA
        #
        # IMPORTANT:
        # farmer.html uses name="other_cost"
        # ----------------------------------------------------

        input_document = {

            "farmer_id":
                farmer_id,

            "farm_id":
                farm_id,

            "record_id":
                record_id,

            "input_id":
                input_id,

            "seed_cost":
                request.form.get(
                    "seed_cost",
                    ""
                ),

            "fertilizer_cost":
                request.form.get(
                    "fertilizer_cost",
                    ""
                ),

            "pesticide_cost":
                request.form.get(
                    "pesticide_cost",
                    ""
                ),

            "labour_cost":
                request.form.get(
                    "labour_cost",
                    ""
                ),

            "irrigation_cost":
                request.form.get(
                    "irrigation_cost",
                    ""
                ),

            "machinery_cost":
                request.form.get(
                    "machinery_cost",
                    ""
                ),

            "other_cultivation_cost":
                request.form.get(
                    "other_cost",
                    ""
                )
        }


        # ----------------------------------------------------
        # SAVE RECORDS TO MONGODB
        # ----------------------------------------------------

        farmers_collection.insert_one(
            farmer_document
        )

        farms_collection.insert_one(
            farm_document
        )

        crop_records_collection.insert_one(
            crop_document
        )

        input_records_collection.insert_one(
            input_document
        )


        # ----------------------------------------------------
        # STORE IDENTIFIERS IN SESSION
        #
        # These identify the farmer whose personal
        # analysis must be displayed.
        # ----------------------------------------------------

        session["farmer_id"] = (
            farmer_id
        )

        session["farm_id"] = (
            farm_id
        )

        session["record_id"] = (
            record_id
        )
        session["farmer_authenticated"] = True


        # ----------------------------------------------------
        # COMPATIBILITY SESSION DATA
        # ----------------------------------------------------

        session["farmer_data"] = {

            "Farmer_ID":
                farmer_id,

            "Farm_ID":
                farm_id,

            "Record_ID":
                record_id,

            "District":
                farmer_document[
                    "district"
                ],

            "Block":
                farmer_document[
                    "block_tehsil"
                ],

            "Block_Tehsil":
                farmer_document[
                    "block_tehsil"
                ],

            "Village":
                farmer_document[
                    "village"
                ],

            "Land_Ownership":
                farmer_document[
                    "land_ownership"
                ],

            "Farm_Area":
                farm_document[
                    "farm_area"
                ],

            "Area_Unit":
                farm_document[
                    "area_unit"
                ],

            "Crop":
                crop_document[
                    "crop"
                ],

            "Cotton_Variety":
                crop_document[
                    "cotton_variety"
                ],

            "Farming_Year":
                crop_document[
                    "farming_year"
                ],

            "Previous_Crop":
                crop_document[
                    "previous_crop"
                ],

            "Cotton_Area":
                crop_document[
                    "cotton_area"
                ],

            "Seed_Cost":
                input_document[
                    "seed_cost"
                ],

            "Fertilizer_Cost":
                input_document[
                    "fertilizer_cost"
                ],

            "Pesticide_Cost":
                input_document[
                    "pesticide_cost"
                ],

            "Labour_Cost":
                input_document[
                    "labour_cost"
                ],

            "Irrigation_Cost":
                input_document[
                    "irrigation_cost"
                ],

            "Machinery_Cost":
                input_document[
                    "machinery_cost"
                ],

            "Other_Cost":
                input_document[
                    "other_cultivation_cost"
                ],

            "Other_Cultivation_Cost":
                input_document[
                    "other_cultivation_cost"
                ],

            "Production":
                crop_document[
                    "production"
                ],

            "Production_Unit":
                crop_document[
                    "production_unit"
                ],

            "Selling_Price":
                crop_document[
                    "selling_price"
                ],

            "Major_Problem":
                crop_document[
                    "major_problem"
                ],

            "Irrigation_Type":
                crop_document[
                    "irrigation_type"
                ],

            "Number_of_Irrigations":
                crop_document[
                    "number_of_irrigations"
                ]
        }


        # ----------------------------------------------------
        # DIRECTLY OPEN THIS FARMER'S ANALYSIS
        # ----------------------------------------------------

        return redirect(
            url_for("analyze")
        )


    return render_template(
        "farmer.html"
    )


# ============================================================
# INDIVIDUAL FARM ANALYSIS
#
# ONE FARMER ONLY
#
# /analyze NEVER performs overall analysis.
# ============================================================
@app.route("/analyze")
def analyze():
    if not session.get("farmer_authenticated"):
        return redirect(url_for("farmer_login"))

    # Your existing analysis code continues here
    

    print(
        "\n=================================================="
    )

    print(
        "INDIVIDUAL FARM ANALYSIS"
    )

    print(
        "=================================================="
    )


    # ----------------------------------------------------
    # GET CURRENT FARMER IDENTIFIERS
    # ----------------------------------------------------

    session_farmer_data = (
        session.get("farmer_data")
        or {}
    )

    farmer_id = (
        session.get("farmer_id")
        or session_farmer_data.get(
            "Farmer_ID"
        )
    )

    farm_id = (
        session.get("farm_id")
        or session_farmer_data.get(
            "Farm_ID"
        )
    )

    record_id = (
        session.get("record_id")
        or session_farmer_data.get(
            "Record_ID"
        )
    )


    # ----------------------------------------------------
    # CHECK SESSION
    # ----------------------------------------------------

    if (
        not farmer_id
        or not farm_id
        or not record_id
    ):

        return """
        <h2>Farmer analysis unavailable</h2>
        <p>No farmer record is currently selected.</p>
        <p>Please register a farmer first.</p>
        <a href="/farmer">Go to Farmer Registration</a>
        """


    print(
        f"Analysing Farmer: {farmer_id}"
    )

    print(
        f"Farm: {farm_id}"
    )

    print(
        f"Record: {record_id}"
    )


    # ----------------------------------------------------
    # RETRIEVE ONLY CURRENT FARMER DATA
    # ----------------------------------------------------

    farmer_doc = (
        farmers_collection.find_one(
            {
                "farmer_id":
                    farmer_id
            }
        )
    )

    farm_doc = (
        farms_collection.find_one(
            {
                "farmer_id":
                    farmer_id,

                "farm_id":
                    farm_id
            }
        )
    )

    crop_doc = (
        crop_records_collection.find_one(
            {
                "farmer_id":
                    farmer_id,

                "farm_id":
                    farm_id,

                "record_id":
                    record_id
            }
        )
    )

    input_doc = (
        input_records_collection.find_one(
            {
                "farmer_id":
                    farmer_id,

                "farm_id":
                    farm_id,

                "record_id":
                    record_id
            }
        )
    )


    # ----------------------------------------------------
    # VERIFY RECORDS
    # ----------------------------------------------------

    if not farmer_doc:

        return f"""
        <h2>Farmer record not found</h2>
        <p>Farmer ID: {farmer_id}</p>
        <a href="/farmer">Register Farmer</a>
        """


    if not farm_doc:

        return f"""
        <h2>Farm record not found</h2>
        <p>Farmer ID: {farmer_id}</p>
        <p>Farm ID: {farm_id}</p>
        """


    if not crop_doc:

        return f"""
        <h2>Crop record not found</h2>
        <p>Farmer ID: {farmer_id}</p>
        <p>Record ID: {record_id}</p>
        """


    if not input_doc:

        return f"""
        <h2>Input record not found</h2>
        <p>Farmer ID: {farmer_id}</p>
        <p>Record ID: {record_id}</p>
        """


    # ----------------------------------------------------
    # BUILD INDIVIDUAL FARM DATA
    # ----------------------------------------------------

    farmer_data = {

        "Farmer_ID":
            farmer_id,

        "Farm_ID":
            farm_id,

        "Record_ID":
            record_id,


        # PROFILE

        "District":
            farmer_doc.get(
                "district",
                ""
            ),

        "Block":
            farmer_doc.get(
                "block_tehsil",
                ""
            ),

        "Block_Tehsil":
            farmer_doc.get(
                "block_tehsil",
                ""
            ),

        "Village":
            farmer_doc.get(
                "village",
                ""
            ),

        "Land_Ownership":
            farmer_doc.get(
                "land_ownership",
                ""
            ),


        # FARM

        "Farm_Area":
            farm_doc.get(
                "farm_area",
                ""
            ),

        "Area_Unit":
            farm_doc.get(
                "area_unit",
                ""
            ),


        # CROP

        "Crop":
            crop_doc.get(
                "crop",
                ""
            ),

        "Cotton_Variety":
            crop_doc.get(
                "cotton_variety",
                ""
            ),

        "Farming_Year":
            crop_doc.get(
                "farming_year",
                ""
            ),

        "Previous_Crop":
            crop_doc.get(
                "previous_crop",
                ""
            ),

        "Cotton_Area":
            crop_doc.get(
                "cotton_area",
                ""
            ),

        "Production":
            crop_doc.get(
                "production",
                ""
            ),

        "Production_Unit":
            crop_doc.get(
                "production_unit",
                ""
            ),

        "Selling_Price":
            crop_doc.get(
                "selling_price",
                ""
            ),

        "Major_Problem":
            crop_doc.get(
                "major_problem",
                ""
            ),

        "Irrigation_Type":
            crop_doc.get(
                "irrigation_type",
                ""
            ),

        "Number_of_Irrigations":
            crop_doc.get(
                "number_of_irrigations",
                ""
            ),


        # INPUT COSTS

        "Seed_Cost":
            input_doc.get(
                "seed_cost",
                ""
            ),

        "Fertilizer_Cost":
            input_doc.get(
                "fertilizer_cost",
                ""
            ),

        "Pesticide_Cost":
            input_doc.get(
                "pesticide_cost",
                ""
            ),

        "Labour_Cost":
            input_doc.get(
                "labour_cost",
                ""
            ),

        "Irrigation_Cost":
            input_doc.get(
                "irrigation_cost",
                ""
            ),

        "Machinery_Cost":
            input_doc.get(
                "machinery_cost",
                ""
            ),

        "Other_Cost":
            input_doc.get(
                "other_cultivation_cost",
                ""
            ),

        "Other_Cultivation_Cost":
            input_doc.get(
                "other_cultivation_cost",
                ""
            )
    }


    # ----------------------------------------------------
    # SAFE NUMERIC CONVERSION
    # ----------------------------------------------------

    def to_float(value):

        try:

            if (
                value is None
                or value == ""
            ):

                return 0.0

            return float(value)

        except (
            ValueError,
            TypeError
        ):

            return 0.0


    # ----------------------------------------------------
    # COST VALUES
    # ----------------------------------------------------

    seed_cost = to_float(
        farmer_data["Seed_Cost"]
    )

    fertilizer_cost = to_float(
        farmer_data["Fertilizer_Cost"]
    )

    pesticide_cost = to_float(
        farmer_data["Pesticide_Cost"]
    )

    labour_cost = to_float(
        farmer_data["Labour_Cost"]
    )

    irrigation_cost = to_float(
        farmer_data["Irrigation_Cost"]
    )

    machinery_cost = to_float(
        farmer_data["Machinery_Cost"]
    )

    other_cost = to_float(
        farmer_data["Other_Cost"]
    )


    # ----------------------------------------------------
    # FARM / CROP VALUES
    # ----------------------------------------------------

    farm_area = to_float(
        farmer_data["Farm_Area"]
    )

    cotton_area = to_float(
        farmer_data["Cotton_Area"]
    )

    production = to_float(
        farmer_data["Production"]
    )

    selling_price = to_float(
        farmer_data["Selling_Price"]
    )


    # ----------------------------------------------------
    # TOTAL CULTIVATION COST
    # ----------------------------------------------------

    total_cost = (
        seed_cost
        + fertilizer_cost
        + pesticide_cost
        + labour_cost
        + irrigation_cost
        + machinery_cost
        + other_cost
    )


    # ----------------------------------------------------
    # ESTIMATED REVENUE
    # ----------------------------------------------------

    total_revenue = (
        production
        * selling_price
    )


    # ----------------------------------------------------
    # ESTIMATED NET RETURN
    # ----------------------------------------------------

    estimated_net_return = (
        total_revenue
        - total_cost
    )


    # ----------------------------------------------------
    # COST PRESSURE
    # ----------------------------------------------------

    if total_revenue > 0:

        cost_pressure = (
            total_cost
            / total_revenue
        ) * 100

    else:

        cost_pressure = 0.0


    # ----------------------------------------------------
    # PESTICIDE COST SHARE
    # ----------------------------------------------------

    if total_cost > 0:

        pesticide_cost_share = (
            pesticide_cost
            / total_cost
        ) * 100

    else:

        pesticide_cost_share = 0.0


    # ----------------------------------------------------
    # PRODUCTION PER COTTON AREA
    # ----------------------------------------------------

    if cotton_area > 0:

        production_per_area = (
            production
            / cotton_area
        )

    else:

        production_per_area = 0.0


    # ----------------------------------------------------
    # COST PER PRODUCTION UNIT
    # ----------------------------------------------------

    if production > 0:

        cost_per_production_unit = (
            total_cost
            / production
        )

    else:

        cost_per_production_unit = 0.0


    # ----------------------------------------------------
    # COTTON AREA SHARE
    # ----------------------------------------------------

    if farm_area > 0:

        cotton_area_share = (
            cotton_area
            / farm_area
        ) * 100

    else:

        cotton_area_share = 0.0


    # ----------------------------------------------------
    # INDIVIDUAL COST SHARES
    # ----------------------------------------------------

    if total_cost > 0:

        seed_cost_share = (
            seed_cost
            / total_cost
        ) * 100

        fertilizer_cost_share = (
            fertilizer_cost
            / total_cost
        ) * 100

        labour_cost_share = (
            labour_cost
            / total_cost
        ) * 100

        irrigation_cost_share = (
            irrigation_cost
            / total_cost
        ) * 100

        machinery_cost_share = (
            machinery_cost
            / total_cost
        ) * 100

        other_cost_share = (
            other_cost
            / total_cost
        ) * 100

    else:

        seed_cost_share = 0.0

        fertilizer_cost_share = 0.0

        labour_cost_share = 0.0

        irrigation_cost_share = 0.0

        machinery_cost_share = 0.0

        other_cost_share = 0.0


    # ========================================================
    # EVIDENCE-BASED OBSERVATIONS
    #
    # IMPORTANT:
    # These are STRINGS because analysis.html expects:
    #
    # {% for observation in analysis.get('Observations') %}
    #
    # They are observations, NOT risk labels.
    # ========================================================

    observations = []


    if total_cost > 0:

        observations.append(
            f"Pesticide expenditure represents "
            f"{pesticide_cost_share:.2f}% of the "
            f"recorded cultivation cost."
        )


    if cotton_area > 0:

        observations.append(
            f"Recorded production is "
            f"{production_per_area:.2f} "
            f"{farmer_data['Production_Unit']} "
            f"per recorded cotton area unit."
        )


    if production > 0:

        observations.append(
            f"Recorded cultivation cost is "
            f"₹{cost_per_production_unit:.2f} "
            f"per production unit."
        )


    if farm_area > 0:

        observations.append(
            f"Cotton occupies "
            f"{cotton_area_share:.2f}% "
            f"of the recorded farm area."
        )


    if total_revenue > 0:

        observations.append(
            f"Recorded cultivation cost represents "
            f"{cost_pressure:.2f}% of the estimated "
            f"revenue based on the recorded production "
            f"and selling price."
        )


    # ========================================================
    # ANALYSIS DICTIONARY
    #
    # THIS IS THE IMPORTANT FIX.
    #
    # analysis.html directly uses:
    #
    # analysis.get(...)
    #
    # Therefore this dictionary MUST be passed to
    # render_template().
    # ========================================================

    analysis = {

        "Total_Cost":
            total_cost,

        "Total_Revenue":
            total_revenue,

        "Estimated_Net_Return":
            estimated_net_return,

        "Cost_Pressure":
            cost_pressure,

        "Pesticide_Cost_Share":
            pesticide_cost_share,

        "Production_Per_Area":
            production_per_area,

        "Cost_Per_Production_Unit":
            cost_per_production_unit,

        "Cotton_Area_Share":
            cotton_area_share,

        "Seed_Cost_Share":
            seed_cost_share,

        "Fertilizer_Cost_Share":
            fertilizer_cost_share,

        "Labour_Cost_Share":
            labour_cost_share,

        "Irrigation_Cost_Share":
            irrigation_cost_share,

        "Machinery_Cost_Share":
            machinery_cost_share,

        "Other_Cost_Share":
            other_cost_share,

        "Observations":
            observations
    }


    # ========================================================
    # SAVE INDIVIDUAL ANALYSIS
    # ========================================================

    analysis_result = {

        "farmer_id":
            farmer_id,

        "farm_id":
            farm_id,

        "record_id":
            record_id,

        "analysis_date":
            datetime.utcnow(),


        # IDENTIFICATION

        "district":
            farmer_data["District"],

        "village":
            farmer_data["Village"],


        # FINANCIAL

        "total_cultivation_cost":
            total_cost,

        "estimated_revenue":
            total_revenue,

        "estimated_net_return":
            estimated_net_return,


        # ANALYTICAL INDICATORS

        "cost_pressure":
            cost_pressure,

        "pesticide_cost_share":
            pesticide_cost_share,

        "production_per_area":
            production_per_area,

        "cost_per_production_unit":
            cost_per_production_unit,

        "cotton_area_share":
            cotton_area_share,


        # COST SHARES

        "seed_cost_share":
            seed_cost_share,

        "fertilizer_cost_share":
            fertilizer_cost_share,

        "labour_cost_share":
            labour_cost_share,

        "irrigation_cost_share":
            irrigation_cost_share,

        "machinery_cost_share":
            machinery_cost_share,

        "other_cost_share":
            other_cost_share,


        # OBSERVATIONS

        "observations":
            observations
    }


    analysis_results_collection.update_one(

        {
            "farmer_id":
                farmer_id,

            "farm_id":
                farm_id,

            "record_id":
                record_id
        },

        {
            "$set":
                analysis_result
        },

        upsert=True
    )


    # ========================================================
    # RENDER INDIVIDUAL FARM ANALYSIS
    # ========================================================

    return render_template(

        "analysis.html",

        farmer_data=farmer_data,

        analysis=analysis,

        total_cost=total_cost,

        total_revenue=total_revenue,

        estimated_net_return=
            estimated_net_return,

        cost_pressure=
            cost_pressure,

        pesticide_cost_share=
            pesticide_cost_share,

        production_per_area=
            production_per_area,

        cost_per_production_unit=
            cost_per_production_unit,

        cotton_area_share=
            cotton_area_share,

        seed_cost_share=
            seed_cost_share,

        fertilizer_cost_share=
            fertilizer_cost_share,

        labour_cost_share=
            labour_cost_share,

        irrigation_cost_share=
            irrigation_cost_share,

        machinery_cost_share=
            machinery_cost_share,

        other_cost_share=
            other_cost_share,

        observations=
            observations
    )

# ============================================================
# COTTON CROP PROBLEM REPORTING
# ============================================================


# ============================================================
# COTTON CROP PROBLEM REPORTING
# ============================================================

@app.route("/report-crop-problem", methods=["POST"])
def report_crop_problem():

    # 1. Verify farmer login
    if not session.get("farmer_authenticated"):
        return redirect(url_for("farmer_login"))

    farmer_id = session.get("farmer_id")
    farm_id = session.get("farm_id")
    record_id = session.get("record_id")

    if not farmer_id or not farm_id or not record_id:
        return "Farmer session information is incomplete.", 400

    # 2. Verify ownership of farmer and crop records
    farmer_doc = farmers_collection.find_one({
        "farmer_id": farmer_id
    })

    crop_doc = crop_records_collection.find_one({
        "farmer_id": farmer_id,
        "farm_id": farm_id,
        "record_id": record_id
    })

    if not farmer_doc or not crop_doc:
        return "Farmer or crop record could not be verified.", 403

    # 3. Read form data
    category = request.form.get("category", "").strip()
    specific_problem = request.form.get("specific_problem", "").strip()
    crop_stage = request.form.get("crop_stage", "").strip()
    symptoms = request.form.get("symptoms", "").strip()
    affected_area = request.form.get("affected_area", "").strip()
    severity = request.form.get("severity", "").strip()
    previous_action = request.form.get("previous_action", "").strip()
    additional_notes = request.form.get("additional_notes", "").strip()

    # 4. Validate required fields
    if not all([
        category,
        specific_problem,
        crop_stage,
        symptoms,
        severity
    ]):
        return "Please complete all required problem-report fields.", 400

    allowed_categories = [
        "Insect Pest",
        "Crop Disease",
        "Nutritional Problem",
        "Soil / Water Problem",
        "Cultivation / Management",
        "Other"
    ]

    allowed_stages = [
        "Germination",
        "Seedling",
        "Vegetative Growth",
        "Flowering",
        "Boll Formation",
        "Boll Opening",
        "Harvesting"
    ]

    allowed_severity = ["Low", "Moderate", "High", "Severe"]

    if category not in allowed_categories:
        return "Invalid problem category.", 400

    if crop_stage not in allowed_stages:
        return "Invalid crop stage.", 400

    if severity not in allowed_severity:
        return "Invalid severity selection.", 400

    # 5. General guidance (not a confirmed diagnosis)
    guidance = {
        "Insect Pest": {
            "possible_causes": [
                "Insect activity or pest population in the field.",
                "Weather and crop-stage conditions favouring pest activity.",
                "Nearby affected crops or inadequate field monitoring."
            ],
            "recommended_actions": [
                "Inspect leaves, shoots, flowers and bolls carefully.",
                "Check the underside of leaves for insects and eggs.",
                "Monitor pest numbers and record affected areas.",
                "Consult a local agricultural expert before selecting any pesticide."
            ],
            "prevention": [
                "Inspect the crop regularly.",
                "Maintain field sanitation and follow recommended crop practices.",
                "Use only locally recommended, label-approved pest-management methods."
            ]
        },

        "Crop Disease": {
            "possible_causes": [
                "Fungal, bacterial or viral infection.",
                "High humidity, prolonged leaf wetness or unsuitable weather.",
                "Infected planting material or crop residues."
            ],
            "recommended_actions": [
                "Observe which plant parts show symptoms and how widely they are spreading.",
                "Avoid unnecessary pesticide or fungicide application.",
                "Seek expert confirmation before choosing a treatment."
            ],
            "prevention": [
                "Use healthy planting material.",
                "Follow recommended spacing and field sanitation practices.",
                "Monitor the crop regularly, especially after humid or wet weather."
            ]
        },

        "Nutritional Problem": {
            "possible_causes": [
                "Possible nutrient deficiency or imbalance.",
                "Soil pH affecting nutrient availability.",
                "Root stress or irrigation-related nutrient uptake problems."
            ],
            "recommended_actions": [
                "Observe whether symptoms appear on older or younger leaves.",
                "Consider soil testing before applying fertilizers.",
                "Ask an agricultural expert to confirm the likely nutrient issue."
            ],
            "prevention": [
                "Use soil-test-based nutrient management.",
                "Apply fertilizers according to recommended doses and crop stage.",
                "Avoid excessive or unbalanced fertilizer application."
            ]
        },

        "Soil / Water Problem": {
            "possible_causes": [
                "Poor drainage or waterlogging.",
                "Water quality or soil salinity concerns.",
                "Irregular irrigation or unsuitable soil moisture conditions."
            ],
            "recommended_actions": [
                "Check soil moisture and drainage in affected areas.",
                "Review irrigation frequency and water source.",
                "Consider soil or irrigation-water testing."
            ],
            "prevention": [
                "Maintain suitable drainage.",
                "Use irrigation according to crop needs and soil conditions.",
                "Follow soil-test-based soil and water management."
            ]
        },

        "Cultivation / Management": {
            "possible_causes": [
                "Irregular crop-management practices.",
                "Unsuitable timing of field operations.",
                "Irrigation, weed or nutrient-management issues."
            ],
            "recommended_actions": [
                "Review recent field operations and their dates.",
                "Compare practices with locally recommended crop-stage guidance.",
                "Discuss corrective steps with an agricultural expert."
            ],
            "prevention": [
                "Maintain a record of important farm operations.",
                "Follow recommended sowing, irrigation and crop-management schedules.",
                "Monitor crop development regularly."
            ]
        },

        "Other": {
            "possible_causes": [
                "The reported symptoms may have more than one possible explanation.",
                "Environmental, biological or management factors may be involved."
            ],
            "recommended_actions": [
                "Record the symptoms and the areas affected.",
                "Monitor whether the condition is improving or worsening.",
                "Seek agricultural expert assistance for identification."
            ],
            "prevention": [
                "Maintain regular field observations.",
                "Keep records of crop conditions and farm activities.",
                "Follow locally recommended agricultural practices."
            ]
        }
    }

    selected_guidance = guidance[category]

    # 6. Create a unique report
    report_id = uuid4().hex

    problem_report = {
        "report_id": report_id,

        "farmer_id": farmer_id,
        "farm_id": farm_id,
        "record_id": record_id,

        "crop": crop_doc.get("crop", ""),
        "category": category,
        "specific_problem": specific_problem,
        "crop_stage": crop_stage,
        "symptoms": symptoms,
        "affected_area": affected_area,
        "severity": severity,
        "previous_action": previous_action,
        "additional_notes": additional_notes,

        "possible_causes": selected_guidance["possible_causes"],
        "recommended_actions": selected_guidance["recommended_actions"],
        "prevention": selected_guidance["prevention"],

        "report_status": "Submitted",
        "progress_updates": [],

        "reported_at": datetime.utcnow()
    }

    # 7. Save report
    crop_problem_reports_collection.insert_one(problem_report)

    # 8. Open the report result page
    return redirect(
        url_for(
            "crop_problem_result",
            report_id=report_id
        )
    )


# ============================================================
# CROP PROBLEM REPORT RESULT PAGE
# ============================================================

@app.route("/crop-problem-result/<report_id>")
def crop_problem_result(report_id):

    if not session.get("farmer_authenticated"):
        return redirect(url_for("farmer_login"))

    farmer_id = session.get("farmer_id")

    if not farmer_id:
        return redirect(url_for("farmer_login"))

    # Only the owner of this report can view it
    report = crop_problem_reports_collection.find_one({
        "report_id": report_id,
        "farmer_id": farmer_id
    })

    if not report:
        return "Report not found or access denied.", 404

    return render_template(
        "crop-problem-result.html",
        report=report
    )

@app.route("/farmer-dashboard")
def farmer_dashboard():
    if not session.get("farmer_authenticated"):
        return redirect(url_for("farmer_login"))

    farmer_id = session.get("farmer_id")

    # Fetch only this farmer's own information
    farmer = farmers_collection.find_one({"farmer_id": farmer_id})

    if not farmer:
        session.clear()
        return redirect(url_for("farmer_login"))

    farms = list(
        farms_collection.find({"farmer_id": farmer_id})
    )

    crop_records = list(
        crop_records_collection.find({"farmer_id": farmer_id})
    )

    reports = list(
        crop_problem_reports_collection.find(
            {"farmer_id": farmer_id}
        ).sort("reported_at", -1)
    )

    return render_template(
        "farmer-dashboard.html",
        farmer=farmer,
        farms=farms,
        crop_records=crop_records,
        reports=reports
    )


@app.route("/select-crop-record", methods=["POST"])
def select_crop_record():
    if not session.get("farmer_authenticated"):
        return redirect(url_for("farmer_login"))

    farmer_id = session.get("farmer_id")
    farm_id = request.form.get("farm_id", "").strip()
    record_id = request.form.get("record_id", "").strip()

    if not farm_id or not record_id:
        return redirect(url_for("farmer_dashboard"))

    # Verify that this farm belongs to the logged-in farmer
    farm_doc = farms_collection.find_one({
        "farmer_id": farmer_id,
        "farm_id": farm_id
    })

    # Verify that this crop record belongs to the same farmer and farm
    crop_doc = crop_records_collection.find_one({
        "farmer_id": farmer_id,
        "farm_id": farm_id,
        "record_id": record_id
    })

    if not farm_doc or not crop_doc:
        return redirect(url_for("farmer_dashboard"))

    # Set the selected record for the analysis page
    session["farm_id"] = farm_id
    session["record_id"] = record_id

    return redirect(url_for("analyze"))

# ============================================================
# EXISTING FARMER LOGIN
# ============================================================

@app.route("/farmer-login", methods=["GET", "POST"])
def farmer_login():

    if request.method == "POST":

        farmer_id = request.form.get(
            "farmer_id", ""
        ).strip().upper()

        password = request.form.get(
            "password", ""
        )

        if not farmer_id or not password:
            return render_template(
                "farmer-login.html",
                error="Please enter both Farmer ID and password."
            )

        # Find farmer
        farmer_doc = farmers_collection.find_one({
            "farmer_id": farmer_id
        })

        # Verify password
        if (
            not farmer_doc
            or not farmer_doc.get("password_hash")
            or not check_password_hash(
                farmer_doc["password_hash"],
                password
            )
        ):
            return render_template(
                "farmer-login.html",
                error="Invalid Farmer ID or password."
            )

        # Find associated farm
        farm_doc = farms_collection.find_one({
            "farmer_id": farmer_id
        })

        # Find associated crop record
        crop_doc = crop_records_collection.find_one({
            "farmer_id": farmer_id
        })

        if not farm_doc or not crop_doc:
            return render_template(
                "farmer-login.html",
                error="Farm or crop records could not be found."
            )

        # Start a fresh authenticated session
        session.clear()

        session["farmer_id"] = farmer_id
        session["farm_id"] = farm_doc.get("farm_id")
        session["record_id"] = crop_doc.get("record_id")
        session["farmer_authenticated"] = True

        return redirect(url_for("farmer_dashboard"))

    return render_template("farmer-login.html")



# ============================================================
# AGRICULTURAL INTELLIGENCE PORTAL
#
# OVERALL ANALYSIS
#
# IMPORTANT:
#
# This route intentionally analyses ALL collected records.
#
# /analyze  = ONE FARMER
# /analytics = ALL FARMERS

# ============================================================
# AGRICULTURAL INTELLIGENCE PORTAL
# ============================================================

@app.route("/analytics")
def analytics():

    selected_district = request.args.get(
        "district",
        ""
    ).strip()

    print("\n==================================================")
    print("AGROREFORM AGRICULTURAL INTELLIGENCE PORTAL")
    print("MULTI-FARMER AREA-WISE ANALYSIS")
    print("==================================================")

    # ====================================================
    # HELPER FUNCTIONS
    # ====================================================

    def safe_float(value):

        try:
            return float(value)

        except (ValueError, TypeError):
            return 0.0


    def clean_text(value, default="Unknown"):

        if value is None:
            return default

        value = str(value).strip()

        if value == "":
            return default

        return value


    # ====================================================
    # LOAD DATA FROM MONGODB
    # ====================================================

    farmer_records = list(
        farmers_collection.find({})
    )

    farm_records = list(
        farms_collection.find({})
    )

    crop_records = list(
        crop_records_collection.find({})
    )

    input_records = list(
        input_records_collection.find({})
    )


    # ====================================================
    # BASIC COUNTS
    # ====================================================

    total_farmers = len(
        farmer_records
    )

    total_farms = len(
        farm_records
    )

    total_crop_records = len(
        crop_records
    )


    # ====================================================
    # INTERNAL FARMER → LOCATION MAPPING
    #
    # farmer_id is used ONLY internally to connect
    # MongoDB records.
    #
    # It is NOT sent to the analytics dashboard.
    # ====================================================

    farmer_location_map = {}

    for farmer in farmer_records:

        farmer_id = farmer.get(
            "farmer_id"
        )

        district = clean_text(
            farmer.get("district")
        )

        block = clean_text(
            farmer.get("block")
        )

        village = clean_text(
            farmer.get("village")
        )

        if farmer_id:

            farmer_location_map[
                farmer_id
            ] = {

                "district": district,

                "block": block,

                "village": village
            }


    # ====================================================
    # DISTRICT-WISE FARMER COUNTS
    # ====================================================

    district_farmer_counts = {}

    for farmer in farmer_records:

        district = clean_text(
            farmer.get("district")
        )

        district_farmer_counts[district] = (

            district_farmer_counts.get(
                district,
                0
            )
            + 1
        )


    # ====================================================
    # AVAILABLE DISTRICTS
    # ====================================================

    available_districts = sorted(
        district_farmer_counts.keys()
    )


    # ====================================================
    # DISTRICT ANALYSIS STRUCTURE
    # ====================================================

    district_analysis = {}


    def create_district(district):

        if district not in district_analysis:

            district_analysis[district] = {

                "farmers": 0,

                "farms": 0,

                "crop_records": 0,

                "area": 0.0,

                "production": 0.0,

                "revenue": 0.0,

                "cost": 0.0,

                "seed_cost": 0.0,

                "fertilizer_cost": 0.0,

                "pesticide_cost": 0.0,

                "labour_cost": 0.0,

                "irrigation_cost": 0.0,

                "machinery_cost": 0.0,

                "other_cost": 0.0,

                "problem_counts": {},

                "irrigation_counts": {},

                "block_counts": {},

                "village_counts": {}
            }


    # ====================================================
    # PROCESS FARMER LOCATION DATA
    # ====================================================

    for district, count in district_farmer_counts.items():

        create_district(district)

        district_analysis[
            district
        ]["farmers"] = count


        for farmer in farmer_records:

            farmer_district = clean_text(
                farmer.get("district")
            )

            if farmer_district != district:
                continue

            block = clean_text(
                farmer.get("block")
            )

            village = clean_text(
                farmer.get("village")
            )

            district_analysis[
                district
            ]["block_counts"][block] = (

                district_analysis[
                    district
                ]["block_counts"].get(
                    block,
                    0
                )
                + 1
            )

            district_analysis[
                district
            ]["village_counts"][village] = (

                district_analysis[
                    district
                ]["village_counts"].get(
                    village,
                    0
                )
                + 1
            )


    # ====================================================
    # OVERALL AGRICULTURAL TOTALS
    # ====================================================

    total_cotton_area = 0.0

    total_production = 0.0

    total_revenue = 0.0

    total_cultivation_cost = 0.0


    # ====================================================
    # COST FIELDS
    # ====================================================

    cost_fields = [

        "seed_cost",

        "fertilizer_cost",

        "pesticide_cost",

        "labour_cost",

        "irrigation_cost",

        "machinery_cost",

        "other_cultivation_cost"
    ]


    # ====================================================
    # PROCESS CROP RECORDS
    # ====================================================

    for record in crop_records:

        farmer_id = record.get(
            "farmer_id"
        )

        location = farmer_location_map.get(
            farmer_id,
            {}
        )

        district = clean_text(
            record.get(
                "district",
                location.get("district")
            )
        )

        create_district(district)


        # -----------------------------------------------
        # AREA
        # -----------------------------------------------

        area = safe_float(
            record.get(
                "cotton_area",
                0
            )
        )


        # -----------------------------------------------
        # PRODUCTION
        # -----------------------------------------------

        production = safe_float(
            record.get(
                "production",
                0
            )
        )


        # -----------------------------------------------
        # SELLING PRICE
        # -----------------------------------------------

        selling_price = safe_float(
            record.get(
                "selling_price",
                0
            )
        )


        # -----------------------------------------------
        # REVENUE
        #
        # This assumes production and selling price
        # use compatible units.
        # -----------------------------------------------

        revenue = (
            production
            * selling_price
        )


        # -----------------------------------------------
        # UPDATE OVERALL VALUES
        # -----------------------------------------------

        total_cotton_area += area

        total_production += production

        total_revenue += revenue


        # -----------------------------------------------
        # UPDATE DISTRICT VALUES
        # -----------------------------------------------

        district_analysis[
            district
        ]["area"] += area

        district_analysis[
            district
        ]["production"] += production

        district_analysis[
            district
        ]["revenue"] += revenue

        district_analysis[
            district
        ]["crop_records"] += 1


        # -----------------------------------------------
        # MAJOR PROBLEM
        # -----------------------------------------------

        problem = clean_text(
            record.get(
                "major_problem"
            ),
            "Not Recorded"
        )

        district_analysis[
            district
        ]["problem_counts"][problem] = (

            district_analysis[
                district
            ]["problem_counts"].get(
                problem,
                0
            )
            + 1
        )


        # -----------------------------------------------
        # IRRIGATION
        # -----------------------------------------------

        irrigation_type = clean_text(
            record.get(
                "irrigation_type"
            ),
            "Not Recorded"
        )

        district_analysis[
            district
        ]["irrigation_counts"][
            irrigation_type
        ] = (

            district_analysis[
                district
            ]["irrigation_counts"].get(
                irrigation_type,
                0
            )
            + 1
        )


    # ====================================================
    # PROCESS INPUT / COST RECORDS
    # ====================================================

    for record in input_records:

        farmer_id = record.get(
            "farmer_id"
        )

        location = farmer_location_map.get(
            farmer_id,
            {}
        )

        district = clean_text(
            record.get(
                "district",
                location.get("district")
            )
        )

        create_district(district)


        # -----------------------------------------------
        # INDIVIDUAL COST COMPONENTS
        # -----------------------------------------------

        seed_cost = safe_float(
            record.get(
                "seed_cost",
                0
            )
        )

        fertilizer_cost = safe_float(
            record.get(
                "fertilizer_cost",
                0
            )
        )

        pesticide_cost = safe_float(
            record.get(
                "pesticide_cost",
                0
            )
        )

        labour_cost = safe_float(
            record.get(
                "labour_cost",
                0
            )
        )

        irrigation_cost = safe_float(
            record.get(
                "irrigation_cost",
                0
            )
        )

        machinery_cost = safe_float(
            record.get(
                "machinery_cost",
                0
            )
        )

        other_cost = safe_float(
            record.get(
                "other_cultivation_cost",
                0
            )
        )


        # -----------------------------------------------
        # TOTAL COST
        # -----------------------------------------------

        record_cost = (

            seed_cost
            + fertilizer_cost
            + pesticide_cost
            + labour_cost
            + irrigation_cost
            + machinery_cost
            + other_cost
        )


        total_cultivation_cost += (
            record_cost
        )


        # -----------------------------------------------
        # UPDATE DISTRICT COSTS
        # -----------------------------------------------

        data = district_analysis[
            district
        ]

        data["cost"] += record_cost

        data["seed_cost"] += seed_cost

        data["fertilizer_cost"] += fertilizer_cost

        data["pesticide_cost"] += pesticide_cost

        data["labour_cost"] += labour_cost

        data["irrigation_cost"] += irrigation_cost

        data["machinery_cost"] += machinery_cost

        data["other_cost"] += other_cost


    # ====================================================
    # DISTRICT METRICS
    # ====================================================

    district_production = {}

    district_yield = {}

    district_cost = {}

    district_revenue = {}

    district_return = {}

    district_area = {}


    for district, data in district_analysis.items():

        area = data["area"]

        production = data["production"]

        cost = data["cost"]

        revenue = data["revenue"]


        # -----------------------------------------------
        # YIELD / ACRE
        # -----------------------------------------------

        if area > 0:

            yield_per_acre = (
                production
                / area
            )

            cost_per_acre = (
                cost
                / area
            )

            return_per_acre = (
                (revenue - cost)
                / area
            )

        else:

            yield_per_acre = 0.0

            cost_per_acre = 0.0

            return_per_acre = 0.0


        net_return = (
            revenue
            - cost
        )


        data["yield_per_acre"] = (
            yield_per_acre
        )

        data["cost_per_acre"] = (
            cost_per_acre
        )

        data["net_return"] = (
            net_return
        )

        data["return_per_acre"] = (
            return_per_acre
        )


        # -----------------------------------------------
        # PESTICIDE COST RATIO
        # -----------------------------------------------

        if cost > 0:

            pesticide_ratio = (

                data["pesticide_cost"]
                / cost
            ) * 100

            fertilizer_ratio = (

                data["fertilizer_cost"]
                / cost
            ) * 100

        else:

            pesticide_ratio = 0.0

            fertilizer_ratio = 0.0


        data["pesticide_cost_ratio"] = (
            pesticide_ratio
        )

        data["fertilizer_cost_ratio"] = (
            fertilizer_ratio
        )


        # -----------------------------------------------
        # SAVE SIMPLE DISTRICT DICTIONARIES
        # -----------------------------------------------

        district_production[district] = (
            round(production, 2)
        )

        district_yield[district] = (
            round(yield_per_acre, 2)
        )

        district_cost[district] = (
            round(cost_per_acre, 2)
        )

        district_revenue[district] = (
            round(revenue, 2)
        )

        district_return[district] = (
            round(return_per_acre, 2)
        )

        district_area[district] = (
            round(area, 2)
        )


    # ====================================================
    # PUNJAB REFERENCE METRICS
    #
    # Calculated from all available AgroReForm records.
    #
    # These are project-database reference values,
    # NOT government agricultural benchmarks.
    # ====================================================

    if total_cotton_area > 0:

        average_yield_per_acre = (

            total_production
            / total_cotton_area
        )

        average_cost_per_acre = (

            total_cultivation_cost
            / total_cotton_area
        )

        average_return_per_acre = (

            (
                total_revenue
                - total_cultivation_cost
            )
            / total_cotton_area
        )

    else:

        average_yield_per_acre = 0.0

        average_cost_per_acre = 0.0

        average_return_per_acre = 0.0


    total_net_return = (

        total_revenue
        - total_cultivation_cost
    )


    # ====================================================
    # MULTI-FARMER PATTERN DETECTION
    #
    # IMPORTANT:
    # These are statistical indicators based on the
    # available AgroReForm records.
    #
    # They are NOT proof of causation.
    # ====================================================

    pattern_flagged_districts = 0


    for district, data in district_analysis.items():

        patterns = []


        # -----------------------------------------------
        # PATTERN 1
        # ECONOMIC STRESS PATTERN
        # -----------------------------------------------

        if (

            data["cost_per_acre"]
            > average_cost_per_acre

            and

            data["return_per_acre"]
            < average_return_per_acre

        ):

            patterns.append({

                "type":
                    "Economic Stress Pattern",

                "reason":
                    "Cultivation cost per acre is above the Punjab project reference while return per acre is below the reference.",

                "evidence": [

                    "Cost per acre: ₹"
                    + f"{data['cost_per_acre']:,.2f}",

                    "Punjab reference cost per acre: ₹"
                    + f"{average_cost_per_acre:,.2f}",

                    "Return per acre: ₹"
                    + f"{data['return_per_acre']:,.2f}",

                    "Punjab reference return per acre: ₹"
                    + f"{average_return_per_acre:,.2f}"
                ]
            })


        # -----------------------------------------------
        # PATTERN 2
        # INPUT–PRODUCTIVITY PATTERN
        # -----------------------------------------------

        if (

            data["cost_per_acre"]
            > average_cost_per_acre

            and

            data["yield_per_acre"]
            <= average_yield_per_acre

        ):

            patterns.append({

                "type":
                    "Input–Productivity Pattern",

                "reason":
                    "Cultivation expenditure per acre is above the Punjab project reference while recorded yield per acre is not above the reference.",

                "evidence": [

                    "Cost per acre: ₹"
                    + f"{data['cost_per_acre']:,.2f}",

                    "Punjab reference cost per acre: ₹"
                    + f"{average_cost_per_acre:,.2f}",

                    "Yield per acre: "
                    + f"{data['yield_per_acre']:,.2f}",

                    "Punjab reference yield per acre: "
                    + f"{average_yield_per_acre:,.2f}"
                ]
            })


        # -----------------------------------------------
        # PATTERN 3
        # PESTICIDE EXPENDITURE PATTERN
        # -----------------------------------------------

        if (

            data["pesticide_cost_ratio"] >= 20

            and

            data["yield_per_acre"]
            <= average_yield_per_acre

        ):

            patterns.append({

                "type":
                    "Pesticide–Productivity Pattern",

                "reason":
                    "Pesticide expenditure represents a substantial share of recorded cultivation cost while yield per acre is not above the Punjab project reference.",

                "evidence": [

                    "Pesticide cost share: "
                    + f"{data['pesticide_cost_ratio']:.1f}%",

                    "Yield per acre: "
                    + f"{data['yield_per_acre']:.2f}",

                    "Punjab reference yield per acre: "
                    + f"{average_yield_per_acre:.2f}"
                ]
            })


        # -----------------------------------------------
        # PATTERN 4
        # RECORDED CROP-HEALTH CONCERN
        # -----------------------------------------------

        problem_counts = data[
            "problem_counts"
        ]

        health_problem_count = 0


        health_keywords = [

            "low yield",

            "crop failure",

            "whitefly",

            "pink bollworm",

            "bollworm",

            "crop disease",

            "soil health",

            "weather",

            "climate",

            "water",

            "irrigation"
        ]


        for problem, count in problem_counts.items():

            problem_lower = problem.lower()

            for keyword in health_keywords:

                if keyword in problem_lower:

                    health_problem_count += count

                    break


        if (

            data["crop_records"] > 0

            and

            health_problem_count > 0

        ):

            problem_percentage = (

                health_problem_count
                / data["crop_records"]
            ) * 100

            if problem_percentage >= 20:

                patterns.append({

                    "type":
                        "Crop Health Concern Pattern",

                    "reason":
                        "A recurring crop-health or field-condition concern is recorded across multiple submitted crop records.",

                    "evidence": [

                        "Affected crop records: "
                        + str(
                            health_problem_count
                        ),

                        "Total crop records: "
                        + str(
                            data["crop_records"]
                        ),

                        "Recorded concern share: "
                        + f"{problem_percentage:.1f}%"
                    ]
                })


        # -----------------------------------------------
        # STORE PATTERNS
        # -----------------------------------------------

        data["patterns"] = patterns

        data["pattern_count"] = len(
            patterns
        )


        if len(patterns) > 0:

            pattern_flagged_districts += 1


    # ====================================================
    # SELECTED DISTRICT
    # ====================================================

    selected_data = None


    if selected_district:

        selected_data = district_analysis.get(
            selected_district
        )


    # ====================================================
    # SELECTED DISTRICT PATTERNS
    # ====================================================

    selected_patterns = []


    if selected_data:

        selected_patterns = selected_data.get(
            "patterns",
            []
        )


    # ====================================================
    # TOP PROBLEMS FOR SELECTED DISTRICT
    # ====================================================

    selected_problem_counts = {}


    if selected_data:

        selected_problem_counts = dict(
            sorted(
                selected_data[
                    "problem_counts"
                ].items(),
                key=lambda x: x[1],
                reverse=True
            )
        )


    # ====================================================
    # TOP BLOCKS FOR SELECTED DISTRICT
    # ====================================================

    selected_blocks = {}


    if selected_data:

        selected_blocks = dict(
            sorted(
                selected_data[
                    "block_counts"
                ].items(),
                key=lambda x: x[1],
                reverse=True
            )
        )


    # ====================================================
    # TOP VILLAGES FOR SELECTED DISTRICT
    # ====================================================

    selected_villages = {}


    if selected_data:

        selected_villages = dict(
            sorted(
                selected_data[
                    "village_counts"
                ].items(),
                key=lambda x: x[1],
                reverse=True
            )
        )


    # ====================================================
    # OVERALL PROBLEM ANALYSIS
    # ====================================================

    problem_counts = {}


    for record in crop_records:

        problem = clean_text(
            record.get(
                "major_problem"
            ),
            "Not Recorded"
        )

        problem_counts[problem] = (

            problem_counts.get(
                problem,
                0
            )
            + 1
        )


    # ====================================================
    # OVERALL IRRIGATION ANALYSIS
    # ====================================================

    irrigation_patterns = {}


    for record in crop_records:

        irrigation_type = clean_text(
            record.get(
                "irrigation_type"
            ),
            "Not Recorded"
        )

        irrigation_patterns[
            irrigation_type
        ] = (

            irrigation_patterns.get(
                irrigation_type,
                0
            )
            + 1
        )


    # ====================================================
    # CROP-WISE ANALYSIS
    # ====================================================

    crop_analysis = {}


    for record in crop_records:

        crop = clean_text(
            record.get(
                "crop"
            ),
            "Cotton"
        )

        production = safe_float(
            record.get(
                "production",
                0
            )
        )

        area = safe_float(
            record.get(
                "cotton_area",
                0
            )
        )


        if crop not in crop_analysis:

            crop_analysis[crop] = {

                "records": 0,

                "area": 0.0,

                "production": 0.0
            }


        crop_analysis[crop][
            "records"
        ] += 1

        crop_analysis[crop][
            "area"
        ] += area

        crop_analysis[crop][
            "production"
        ] += production


    # ====================================================
    # CROP-WISE YIELD
    # ====================================================

    for crop, data in crop_analysis.items():

        if data["area"] > 0:

            data["yield_per_acre"] = (

                data["production"]
                / data["area"]
            )

        else:

            data["yield_per_acre"] = 0.0


    # ====================================================
    # SORT DISTRICT DATA
    # ====================================================

    district_production = dict(
        sorted(
            district_production.items(),
            key=lambda x: x[1],
            reverse=True
        )
    )


    district_farmer_counts = dict(
        sorted(
            district_farmer_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
    )


    # ====================================================
    # TOTAL DISTRICTS
    # ====================================================

    total_districts = len(
        district_analysis
    )


    # ====================================================
    # RENDER ANALYTICS PORTAL
    # ====================================================

    return render_template(

        "analytics.html",

        # -----------------------------------------------
        # BASIC OVERVIEW
        # -----------------------------------------------

        total_farmers=
            total_farmers,

        total_farms=
            total_farms,

        total_crop_records=
            total_crop_records,

        total_districts=
            total_districts,

        total_cotton_area=
            round(
                total_cotton_area,
                2
            ),

        total_production=
            round(
                total_production,
                2
            ),

        total_cultivation_cost=
            round(
                total_cultivation_cost,
                2
            ),

        total_revenue=
            round(
                total_revenue,
                2
            ),

        total_net_return=
            round(
                total_net_return,
                2
            ),

        average_yield_per_acre=
            round(
                average_yield_per_acre,
                2
            ),

        average_cost_per_acre=
            round(
                average_cost_per_acre,
                2
            ),

        average_return_per_acre=
            round(
                average_return_per_acre,
                2
            ),

        # -----------------------------------------------
        # PATTERN ANALYSIS
        # -----------------------------------------------

        pattern_flagged_districts=
            pattern_flagged_districts,

        risk_flagged_districts=
            pattern_flagged_districts,

        # -----------------------------------------------
        # DISTRICT DATA
        # -----------------------------------------------

        district_analysis=
            district_analysis,

        district_farmer_counts=
            district_farmer_counts,

        district_production=
            district_production,

        district_yield=
            district_yield,

        district_cost=
            district_cost,

        district_revenue=
            district_revenue,

        district_return=
            district_return,

        district_area=
            district_area,

        # -----------------------------------------------
        # DISTRICT SELECTION
        # -----------------------------------------------

        available_districts=
            available_districts,

        selected_district=
            selected_district,

        selected_data=
            selected_data,

        selected_patterns=
            selected_patterns,

        selected_problem_counts=
            selected_problem_counts,

        selected_blocks=
            selected_blocks,

        selected_villages=
            selected_villages,

        # -----------------------------------------------
        # PROBLEM ANALYSIS
        # -----------------------------------------------

        problem_counts=
            problem_counts,

        irrigation_patterns=
            irrigation_patterns,

        # -----------------------------------------------
        # CROP ANALYSIS
        # -----------------------------------------------

        crop_analysis=
            crop_analysis
    )



# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
