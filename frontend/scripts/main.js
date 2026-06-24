// check for form submission
document.getElementById("start_form").addEventListener("submit", validateStart);
let user_session_id = null;

function invalidInput(current_element) {
    current_element.classList.add("shake");
    current_element.style.border = "1px solid " + getComputedStyle(document.documentElement).getPropertyValue("--warning").trim();
    setTimeout(() => {
        current_element.classList.remove("shake");
        if (current_element.isEqualNode(document.getElementById("user_message"))) {
            current_element.style.border = "1px solid " + getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim();
        } else {
            current_element.style.border = "none";
        }
    }, 300);
}
    

// start endpoint
async function validateStart(event) {
    event.preventDefault();
    
    // session parameters
    const session_description_el = document.getElementById("description");
    const session_description = document.getElementById("description").value;

    const session_personality_el = document.getElementById("personality");
    const session_personality = document.getElementById("personality").value;

    const session_difficulty = document.getElementById("customer_type").value;
    const session_interest_level = document.getElementById("interest_level").value;

    if (!session_description) {
        console.log("no value");
        invalidInput(session_description_el);
        return;
    }

    if (!session_personality) {
        invalidInput(session_personality_el);
        return;
    }

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

const objection_map = {
    "price": "Price / budget",
    "timing": "Bad timing",
    "incumbent_vendor": "Has existing vendor",
    "no_need": "Customer doesn't have a need",
    "no_authority": "Not decision maker",
    "trust": "Lack of trust",
    "null": "No current objection",
}

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
    let user_message_el = document.getElementById("user_message");
    let user_message = document.getElementById("user_message").value;

    if (!user_message) {
        invalidInput(user_message_el);
        return;
    }

    console.log(user_message);
    addMessage(user_message, "user");
    addTypingIndicator();


    // clear message text field
    document.getElementById("user_message").value = "";

    document.getElementById("user_message").disabled = true;
    document.getElementById("send_button").disabled = true;

    let input_box = document.getElementById("user_message");
    input_box.style.border = "1px solid " + getComputedStyle(document.documentElement).getPropertyValue("--warning").trim();
    

    document.getElementsByClassName("ood_warning")[0].style.visibility="hidden";


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
        //document.getElementById("user_message").style.removeProperty("border-color");
        document.getElementById("user_message").style.border = "1px solid " + getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim();

        document.getElementsByClassName("messages")[0].scrollTop = document.getElementsByClassName("messages")[0].scrollHeight;

        let classification = document.getElementsByClassName("info-value");

        classification[0].textContent = classification_map[customer_response["classification"]];

        if (customer_response["classification"] !== "N/A") {

            updateDistribution(customer_response["distribution"], customer_response["classification"]);
        }

        if (customer_response["low_confidence"] === true) {
            document.getElementsByClassName("ood_warning")[0].style.visibility="visible";
        }

        let current_objection = document.getElementsByClassName("current_objection");
        current_objection[0].textContent = objection_map[customer_response["objection"]];

        updateInterestLevel(customer_response["interest_level"]);

        let number_turns = document.getElementsByClassName("number_turns");
        number_turns[0].textContent = customer_response["turn_number"];
        
        

    } catch (error) {
        console.log(error.message);
        document.getElementById("user_message").disabled = false;
        document.getElementById("send_button").disabled = false;
    }

}


function populateLeft(description, personality, difficulty, turns, final_interest, most_frequent_class, low_confidence) {

    const fields = [
        ["Description", description],
        ["Personality", personality],
        ["Difficulty", difficulty],
        ["Total turns", turns],
        ["Final interest", final_interest],
        ["Dominant behaviour", most_frequent_class[0]],
        ["Low confidence inputs", low_confidence]
    ];

    const container = document.getElementsByClassName("finish_left")[0];

    fields.forEach(([label, value]) => {
        let l = document.createElement("p");
        let v = document.createElement("p");
        l.classList.add("finish_label")
        v.classList.add("finish_text");
        l.textContent = `${label}`;
        v.textContent = value;
        container.appendChild(l);
        container.appendChild(v);
    });

}

function classificationBreakdown(history, turns) {
    const filtered = history.filter(h => h !== "N/A");

    let class_counts = {
        "WC": 0,
        "OH": 0,
        "FD": 0,
        "AN": 0
    };

    for (let i = 0; i < filtered.length; i++) {
        class_counts[filtered[i]]++;
    }

    let maxKey, maxValue = 0;
    for (const key in class_counts) {
        if (class_counts[key] > maxValue) {
            maxKey = key;
            maxValue = class_counts[key];
        }
    }

    let class_counts_title = document.createElement("p");
    class_counts_title.classList.add("finish_label");
    class_counts_title.textContent = "Class counts";
    document.getElementsByClassName("finish_right")[0].appendChild(class_counts_title);

    if (maxValue === 0) {
        let class_warning = document.createElement("p");
        class_warning.classList.add("finish_text");
        class_warning.textContent = "No classifications detected";
        document.getElementsByClassName("finish_right")[0].appendChild(class_warning);
        return;
    }

    for (const key in class_counts) {
        let bar = document.createElement("div");

        if (key === maxKey) {
            bar.classList.add("winning_score_bar");
        } else {
            bar.classList.add("score_bar");
        }
        

        let width = 0;
        let frame = () => {
            if (width >= class_counts[key]/filtered.length*100) {
                clearInterval(id);
            } else {
                
                width++;
                bar.style.width = width + "%";
            }
        }

        let id = setInterval(frame, 5);

        if (class_counts[key] == 0) {
            bar.style.width = "0%";
        }

        let label = document.createElement("p");
        label.classList.add("finish_text");
        label.textContent = `${key}: ${class_counts[key]}`;
        
        document.getElementsByClassName("finish_right")[0].appendChild(label);
        document.getElementsByClassName("finish_right")[0].appendChild(bar);
    }
}

function interestLineGraph(interest_trajectory) {
    let title = document.createElement("p");
    title.classList.add("finish_label");
    title.textContent = "Interest over time";
    document.getElementsByClassName("finish_right")[0].appendChild(title);

    points = [];

    for (let i = 0; i < interest_trajectory.length; i++) {
        points.push([i, interest_trajectory[i]]);
    }
    
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    const polyline = document.createElementNS("http://www.w3.org/2000/svg", "polyline");

    const container = document.getElementsByClassName("finish_right")[0];
    const svgWidth = container.clientWidth;
    const svgHeight = container.clientHeight/2;

    const paddingLeft = 30;
    const paddingBottom = 50;
    const paddingTop = 30;
    const paddingRight = 50;
    

    const xScale = i => (i / (interest_trajectory.length - 1)) * svgWidth;
    const yScale = v => svgHeight - ((v-1)/4) * svgHeight;

    const pointsString = points.map(([i,v]) => `${xScale(i)}, ${yScale(v)}`).join(" ");

    const yAxis = document.createElementNS("http://www.w3.org/2000/svg", "line");
    yAxis.setAttribute("x1", 0);
    yAxis.setAttribute("y1", 0);
    yAxis.setAttribute("x2", 0);
    yAxis.setAttribute("y2", svgHeight);
    yAxis.setAttribute("stroke", getComputedStyle(document.documentElement).getPropertyValue("--accent").trim());
    yAxis.setAttribute("stroke-width", "3");

    const xAxis = document.createElementNS("http://www.w3.org/2000/svg", "line");
    xAxis.setAttribute("x1", 0);
    xAxis.setAttribute("y1", svgHeight);
    xAxis.setAttribute("x2", svgWidth);
    xAxis.setAttribute("y2", svgHeight);
    xAxis.setAttribute("stroke", getComputedStyle(document.documentElement).getPropertyValue("--accent").trim());
    xAxis.setAttribute("stroke-width", "3");

    svg.appendChild(yAxis);
    svg.appendChild(xAxis);

    polyline.setAttribute("points", pointsString);
    polyline.setAttribute("fill", "none");
    polyline.setAttribute("stroke", getComputedStyle(document.documentElement).getPropertyValue("--text").trim());
    polyline.setAttribute("stroke-width", "3");

    for (let i = 0; i < points.length; i++) {
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", xScale(points[i][0]));
        circle.setAttribute("cy", yScale(points[i][1]));
        circle.setAttribute("r", 4);
        circle.setAttribute("fill", getComputedStyle(document.documentElement).getPropertyValue("--text").trim());
        svg.appendChild(circle);
    }

    

    const yLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
    yLabel.setAttribute("transform", "rotate(-90)");
    yLabel.setAttribute("x", -svgHeight/2-24);
    yLabel.setAttribute("y", -8);
    yLabel.setAttribute("fill", getComputedStyle(document.documentElement).getPropertyValue("--text").trim());
    yLabel.setAttribute("font-size", "12");
    yLabel.textContent = "Interest";

    

    const xLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
    xLabel.setAttribute("x", svgWidth/2-44);
    xLabel.setAttribute("y", svgHeight+16);
    xLabel.setAttribute("fill", getComputedStyle(document.documentElement).getPropertyValue("--text").trim());
    xLabel.setAttribute("font-size", "12");
    xLabel.textContent = "Turns";
    

    svg.setAttribute("viewBox", `${-paddingLeft} ${-paddingTop} ${svgWidth+paddingRight} ${svgHeight+paddingBottom}`);
    

    svg.appendChild(polyline);
    svg.appendChild(yLabel);
    svg.appendChild(xLabel);

    document.getElementsByClassName("finish_right")[0].appendChild(svg);
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

    let backend_response = await response.json();
    console.log(backend_response);

    document.getElementsByClassName("active_session")[0].style.display="none";
    document.getElementsByClassName("finish_session")[0].style.display="flex";


    populateLeft(backend_response["description"], backend_response["personality"], backend_response["difficulty"], backend_response["total_turns"], backend_response["final_interest_level"], backend_response["most_frequent_class"],backend_response["low_confidence_count"]);
    classificationBreakdown(backend_response["classification_history"], backend_response["total_turns"]);
    interestLineGraph(backend_response["interest_trajectory"]);

    old_messages = document.getElementsByClassName("messages")[0].children;
    for (let i = 0; i < old_messages.length; i++) {

        old_messages[i].classList.remove("message");
        old_messages[i].textContent="";
    }

    document.querySelectorAll(".progress_bar").forEach(p => p.remove());
    document.querySelectorAll(".winning_bar").forEach(p => p.remove());
    document.querySelectorAll(".span_distribution_label").forEach(p => p.remove());
    let old_label = document.querySelector(".distribution_label");
    if (old_label) {
        old_label.remove();
    }

    document.getElementsByClassName("ood_warning")[0].style.visibility="hidden";
    

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

    document.getElementsByClassName("current_objection")[0].textContent = objection_map[null];
    document.getElementsByClassName("number_turns")[0].textContent = 0;
    
    document.getElementsByClassName("finish_left")[0].innerHTML = "";
    document.getElementsByClassName("finish_right")[0].innerHTML = "";
}


