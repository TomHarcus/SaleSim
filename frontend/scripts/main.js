// check for form submission
document.getElementById("start_form").addEventListener("submit", validateStart);
let user_session_id = null;

// start endpoint
async function validateStart(event) {
    event.preventDefault();
    
    // session parameters
    const session_description = document.getElementById("description").value;
    const session_personality = document.getElementById("personality").value;

    const session_difficulty = document.getElementById("customer_type").value;
    const session_interest_level = document.getElementById("interest_level").value;

    // create request object to backend
    const request = {
        description: session_description,
        personality: session_personality,
        customer_type: session_difficulty,
        interest_level: parseInt(session_interest_level)
    };

    // start endpoint
    const url = "http://127.0.0.1:8000/start";

    // try and make request
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

        // store returned session id and print
        user_session_id = await response.json();
        console.log(user_session_id);

        // once collected session id go to active session state
        document.getElementsByClassName("start_state")[0].style.display="none";
        document.getElementsByClassName("active_session")[0].style.display="flex";

    } catch (error) {
        console.log(error.message);
    }

}


document.getElementById("send_button").addEventListener("click", sendMessage);

let input = document.getElementById("user_message")
input.addEventListener("keypress", function(event) {
    if (event.key==="Enter") {
        sendMessage(event);
    }
})
async function sendMessage(event) {
    event.preventDefault();
    let user_message = document.getElementById("user_message").value;
    console.log(user_message);

    document.getElementById("user_message").value = "";
}


