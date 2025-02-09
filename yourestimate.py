import streamlit as st

def calculate_cost(copay, coinsurance, oop, oop_max, deductible, deductible_max, contracted_rate, service_code, deductible_type):
    """Calculates patient cost """

    your_cost = 0

    if contracted_rate is None:
        return None

    elif copay == 'CE001' or coinsurance == 'CE001':
        return 0

    elif copay == 'CE002' or coinsurance == 'CE002':
        return contracted_rate

    if deductible_type is None:
        st.warning("Deductible Type is unspecified. Applying default calculation (ded_met).")
        deductible_type = "ded_met"

    if deductible_type == 'ded_waived':
        deductible_max = 0

    if copay is None or copay == 'NA':
        copay = 0
    else:
        try:
            copay = float(copay)
        except ValueError:
            st.error("Invalid copay value. Please enter a number or 'NA'.")
            return None

    if coinsurance is None or coinsurance == 'NA':
        coinsurance = 0
    else:
        try:
            coinsurance = float(coinsurance)
        except ValueError:
            st.error("Invalid coinsurance value. Please enter a number or 'NA'.")
            return None

    if deductible < deductible_max and oop < oop_max:
        ref_cost = deductible + contracted_rate

        if ref_cost < deductible_max and ref_cost < oop_max:
            your_cost = contracted_rate
        elif ref_cost >= deductible_max and ref_cost < oop_max:
            your_cost = copay + (deductible_max - deductible) + (coinsurance / 100) * (contracted_rate - (deductible_max - deductible))
        else:
            your_cost = copay + (deductible_max - deductible) + (coinsurance / 100) * (contracted_rate - (deductible_max - deductible))
            your_cost = min(your_cost, oop_max - oop)

        your_cost = min(your_cost, contracted_rate)

    elif deductible >= deductible_max and oop < oop_max:
        ref_cost = oop + contracted_rate

        if ref_cost < oop_max:
            your_cost = copay + (coinsurance / 100) * contracted_rate
        else:
            your_cost = copay + (coinsurance / 100) * contracted_rate
            your_cost = min(your_cost, oop_max - oop)

        your_cost = min(your_cost, contracted_rate)

    elif deductible >= deductible_max and oop >= oop_max:
        your_cost = 0 if oop_max!= 0 else (coinsurance / 100) * contracted_rate + copay
        your_cost = min(your_cost, contracted_rate)

    else:
        your_cost = 0

    return your_cost


# Streamlit app
st.title("Patient Cost Estimator")

place_of_service_options = {
    1: "Pharmacy",
    2: "Telemedicine",
    3: "Outpatient",
    4: "Office",
    5: "Inpatient",
    6: "Emergency Room",
    7: "Others",
}

service_code = st.selectbox("Place of Service", options=list(place_of_service_options.values()), format_func=lambda x: x)  # Use dictionary values for display

# Get the corresponding service code (integer)
service_code_int = list(place_of_service_options.keys())[list(place_of_service_options.values()).index(service_code)]


col1, col2 = st.columns(2)
with col1:
    copay = st.text_input(f"Copay for {service_code} (NA if none)")
with col2:
    coinsurance = st.text_input(f"Coinsurance for {service_code} (NA if none)")


oop = st.number_input("Out-of-Pocket (OOP) Total", min_value=0.0, value=0.0)
oop_max = st.number_input("OOP Maximum", min_value=0.0, value=10000.0)
deductible = st.number_input("Deductible Total", min_value=0.0, value=0.0)
deductible_max = st.number_input("Deductible Maximum", min_value=0.0, value=5000.0)
contracted_rate = st.number_input("Contracted Rate", min_value=0.0, value=0.0)
deductible_type = st.selectbox("Deductible Type", ["ded_waived", None])

if st.button("Calculate Cost"):
    if copay is None or coinsurance is None:
        st.warning("Please enter valid copay and coinsurance amounts. Enter NA if none.")
    else:
        estimated_cost = calculate_cost(copay, coinsurance, oop, oop_max, deductible, deductible_max, contracted_rate, service_code_int, deductible_type)
        if estimated_cost is not None:
            st.write(f"Estimated Cost: ${estimated_cost:.2f}")