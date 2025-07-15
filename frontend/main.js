// ============================
// 1. CSRF Token Getter (Django)
// ============================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        document.cookie.split(';').forEach(cookie => {
            const trimmed = cookie.trim();
            if (trimmed.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
            }
        });
    }
    return cookieValue;
}

// ============================
// 2. POST Request to Backend
// ============================
async function prendreRendezVous(formData) {
    const csrftoken = getCookie('csrftoken');
    try {
        const response = await fetch('http://127.0.0.1:8000/prendre-rendez-vous/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify(formData)
        });

        return await response.json();
    } catch (error) {
        console.error('Erreur réseau lors de la prise de RDV :', error);
        return { status: 'error', message: 'Erreur de connexion serveur.' };
    }
}

// ============================
// 3. Form Submit Handler
// ============================
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('appointment-form');

    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const nom = document.getElementById('nom')?.value.trim();
        const prenom = document.getElementById('prenom')?.value.trim();
        const telephone = document.getElementById('telephone')?.value.trim();
        const email = document.getElementById('email')?.value.trim();
        const date_souhaitee = document.getElementById('date_souhaitee')?.value;
        const service = document.getElementById('service_id')?.value;
        const message = document.getElementById('message')?.value.trim();
        const consentement = document.getElementById('consentement')?.checked;

        // Champs requis
        if (!nom || !prenom || !telephone || !email || !date_souhaitee || !service || !consentement) {
            alert("Merci de remplir tous les champs obligatoires et d'accepter le consentement.");
            return;
        }

        const serviceId = parseInt(service);
        if (isNaN(serviceId)) {
            alert("Le service sélectionné est invalide.");
            return;
        }

        const formData = {
            nom,
            prenom,
            telephone,
            email,
            date_souhaitee,
            service: serviceId,
            message
        };

        const result = await prendreRendezVous(formData);

        if (result.status === 'ok') {
            alert("✅ Votre rendez-vous a été enregistré avec succès !");
            form.reset();
        } else {
            alert("❌ Une erreur est survenue : " + result.message);
        }
    });
});
