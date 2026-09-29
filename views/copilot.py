import streamlit as st


st.markdown("# AI Clinical Copilot")

st.caption(
    "Ask questions about the current patient, "
    "HT prediction, explanations and "
    "AI-supported recommendations."
)


patient = st.session_state.get(
    "patient"
)


if patient is None:

    st.warning(
        "Create a patient digital twin first."
    )

    st.stop()


with st.expander(
    "Information available to the Copilot"
):

    st.json({

        "patient":
            patient,

        "HT_probability":
            st.session_state.get(
                "ht_probability"
            ),

        "model":
            st.session_state.model_version,

        "recommendation":
            st.session_state.get(
                "recommendation"
            )
    })


question = st.chat_input(
    "Ask about this patient..."
)


if question:

    with st.chat_message(
        "user"
    ):

        st.write(
            question
        )


    with st.chat_message(
        "assistant"
    ):

        st.write(
            "The LLM and clinical RAG layer "
            "will be connected here in the "
            "next integration step."
        )