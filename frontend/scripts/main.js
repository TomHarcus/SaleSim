document.getElementById("start_form").addEventListener("submit", validateStart)

function validateStart(event) {
    event.preventDefault();
    
    const description = document.getElementById("description").value;
    const personality = document.getElementById("personality").value;

    const difficulty = document.getElementById("customer_type").value;
    const interest_level = document.getElementById("interest_level").value;

    console.log(description);
    console.log(personality);
    console.log(difficulty);
    console.log(interest_level);
}