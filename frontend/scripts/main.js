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
            "Content-Type": "application/json"
        },
        body: JSON.stringify(request)
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

        updateInterestLevel(session_interest_level);

    } catch (error) {
        console.log(error.message);
    }

}

const classification_map = {
    "OH": "Objection handling",
    "AN": "Anchoring",
    "FD": "Feature dumping",
    "WC": "Weak concession",
    "N/A": "N/A"
};

function addTypingIndicator() {
    let typing_indicator = document.createElement("div");
    typing_indicator.classList.add("typing", "message", "prospect");
    typing_indicator.id = "typing_indicator";
    for (let i = 0; i < 3; i++) {
        let dot = document.createElement("span");
        typing_indicator.appendChild(dot);
    }

    document.getElementsByClassName("messages")[0].appendChild(typing_indicator);
}

function removeTypingIndicator() {
    document.getElementById("typing_indicator").remove();
}

function addMessage(content, type) {
    let new_message = document.createElement("div");
    new_message.classList.add("message", type);
    new_message.textContent = content;

    document.getElementsByClassName("messages")[0].appendChild(new_message);

}

function updateDistribution(distribution, classification) {
    document.querySelectorAll(".progress_bar").forEach(p => p.remove());
    document.querySelectorAll(".winning_bar").forEach(p => p.remove());
    document.querySelectorAll(".span_distribution_label").forEach(p => p.remove());
    let old_label = document.querySelector(".distribution_label");
    if (old_label) {
        old_label.remove();
    }

    let current_distribution = document.createElement("div");
    current_distribution.classList.add("distribution_label")
    current_distribution.textContent = "Class Distribution";
    
    document.getElementsByClassName("information")[0].insertBefore(current_distribution, document.querySelector(".info-label"));
    for (const key in distribution) {
        let bar = document.createElement("div");
        if (key === classification) {
            bar.classList.add("winning_bar");
        } else {
            bar.classList.add("progress_bar");
        }
        
        let width = 0;
        let frame = () => {
            if (width >= distribution[key]*100) {
            clearInterval(id);
        } else {
            width ++;
            bar.style.width = width + "%";
        }
        }

        let id = setInterval(frame, 5);

        if (distribution[key] === 0) {
            bar.style.width = "0%";
        }
        let label = document.createElement("span");
        label.classList.add("span_distribution_label");
        label.textContent = `${key}: ${(Math.round(distribution[key]*100))}%`;
        
        document.getElementsByClassName("information")[0].insertBefore(label, document.querySelector(".info-label"));
        document.getElementsByClassName("information")[0].insertBefore(bar, document.querySelector(".info-label"));    
    }
}

function updateInterestLevel(current_interest_level) {
    interest_level = document.getElementsByClassName("interest-dots")[0].children;

    for (let i = 0; i < interest_level.length; i++) {
        if (i < current_interest_level) {
            interest_level[i].classList.add("active");
        } else {
            interest_level[i].classList.remove("active");
        }
    }
   
}


// two ways to send message: click send button or press enter key
document.getElementById("send_button").addEventListener("click", sendMessage);

let input = document.getElementById("user_message")
input.addEventListener("keypress", function(event) {
    if (event.key==="Enter") {
        sendMessage(event);
    }
})



// send message 
async function sendMessage(event) {
    event.preventDefault();
    let user_message = document.getElementById("user_message").value;
    console.log(user_message);
    addMessage(user_message, "user");
    addTypingIndicator();


    // clear message text field
    document.getElementById("user_message").value = "";

    document.getElementById("user_message").disabled = true;
    document.getElementById("send_button").disabled = true;

    const request = {
        session_id: user_session_id,
        content: user_message
    };

    const url = "http://127.0.0.1:8000/message";

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(request) })

        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        let customer_response = await response.json();
        removeTypingIndicator();
        addMessage(customer_response["content"], "prospect");
        console.log(customer_response);

        document.getElementById("user_message").disabled = false;
        document.getElementById("send_button").disabled = false;

        document.getElementsByClassName("messages")[0].scrollTop = document.getElementsByClassName("messages")[0].scrollHeight;

        let classification = document.getElementsByClassName("info-value");

        classification[0].textContent = classification_map[customer_response["classification"]];

        if (customer_response["classification"] !== "N/A") {

            updateDistribution(customer_response["distribution"], customer_response["classification"]);
        }

        updateInterestLevel(customer_response["interest_level"]);
        
        

    } catch (error) {
        console.log(error.message);
        document.getElementById("user_message").disabled = false;
        document.getElementById("send_button").disabled = false;
    }

}

document.getElementById("end_session").addEventListener("click", endSession);

async function endSession(event) {
    event.preventDefault();

    const url = "http://127.0.0.1:8000/end"

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({session_id: user_session_id})
        })

    if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
    }

    document.getElementsByClassName("active_session")[0].style.display="none";
    document.getElementsByClassName("finish_session")[0].style.display="flex";

    old_messages = document.getElementsByClassName("messages")[0].children;
    for (let i = 0; i < old_messages.length; i++) {

        old_messages[i].classList.remove("message");
        old_messages[i].textContent="";
    }
    

    } catch (error) {
        console.log(error.message);
    }
    console.log("session ended");
}

document.getElementById("restart_button").addEventListener("click", startNewSession);

function startNewSession(event) {
    document.getElementsByClassName("finish_session")[0].style.display="none";
    document.getElementsByClassName("start_state")[0].style.display="flex";
    user_session_id = null;

    let classification = document.getElementsByClassName("info-value");
    classification[0].textContent = classification_map["N/A"];
}


