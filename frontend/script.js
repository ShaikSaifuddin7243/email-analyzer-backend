fetch('https://email-analyzer-backend-dbo0.onrender.com/api/emails')
    .then(response => response.json())
    .then(data => {
        
        document.getElementById('email-count').innerText = `Total Analyzed: ${data.total_emails}`;
        
        const container = document.getElementById('email-container');
        container.innerHTML = ''; 

        let newsCount = 0;
        let realCount = 0;

        data.emails.forEach(email => {
            if (email.stats.is_newsletter) {
                newsCount++;
            } else {
                realCount++;
            }

            const isNews = email.stats.is_newsletter ? 'newsletter' : '';
            const tagHtml = email.stats.is_newsletter ? '<span class="tag">Newsletter</span>' : '';

            const card = `
                <div class="email-card ${isNews}">
                    <h3>${email.subject} ${tagHtml}</h3>
                    <div class="meta">
                        <strong>From:</strong> ${email.sender_name} (${email.sender_email})<br>
                        <strong>Length:</strong> ${email.stats.char_count} characters
                    </div>
                </div>
            `;
            container.innerHTML += card;
        });

        const ctx = document.getElementById('newsletterChart').getContext('2d');
        new Chart(ctx, {
            type: 'pie', 
            data: {
                labels: ['Newsletters', 'Real Emails'],
                datasets: [{
                    data: [newsCount, realCount], 
                    backgroundColor: ['#ff4757', '#2ed573'] 
                }]
            }
        });

    })
    .catch(error => console.error('Error fetching data:', error));