document.getElementById("start_form").addEventListener("submit", validateStart);
let user_session_id = null;

async function validateStart(event) {
    event.preventDefault();
    
    const session_description = document.getElementById("description").value;
    const session_personality = document.getElementById("personality").value;

    const session_difficulty = document.getElementById("customer_type").value;
    const session_interest_level = document.getElementById("interest_level").value;

    const request = {
        description: session_description,
        personality: session_personality,
        customer_type: session_difficulty,
        interest_level: parseInt(session_interest_level)
    };

    const url = "http://127.0.0.1:8000/start";

    try {
        const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
        });

        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        user_session_id = await response.json();
        console.log(user_session_id);
        document.getElementsByClassName("start_state")[0].style.display="none";
        document.getElementsByClassName("active_session")[0].style.display="flex";

        

        

    } catch (error) {
        console.log(error.message);
    }

}