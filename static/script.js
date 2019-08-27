async function command(url) {
    logger = document.getElementById('log');

    let response = null;
    
    try {
        response = await fetch(url);

        if (!response.ok) {
            const text = await response.text();

            throw new Error(text);
        } else {
            let data = await response.json()

            logger.innerHTML += '<p>' + data.message + '</p>';
        }
    } catch (error) {
        logger.innerHTML += '<p class="error">' + error + '</p>';
    }
}
