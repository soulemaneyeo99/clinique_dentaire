// ===============================================
// 1. CSRF Token Helper (sécurisé pour Django)
// ===============================================
function getCookie(name) {
  const cookies = document.cookie?.split(';') || [];
  for (const cookie of cookies) {
    const trimmed = cookie.trim();
    if (trimmed.startsWith(`${name}=`)) {
      return decodeURIComponent(trimmed.substring(name.length + 1));
    }
  }
  return null;
}

// ===============================================
// 2. Handler principal du formulaire de RDV
// ===============================================
document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('#appointment-form');
  if (!form) return;

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    // =====================
    // A. Collecte des champs
    // =====================
    const nom = form.nom?.value.trim();
    const prenom = form.prenom?.value.trim();
    const telephone = form.telephone?.value.trim();
    const email = form.email?.value.trim();
    const date_souhaitee = form.date_souhaitee?.value;
    const service = parseInt(form.service_id?.value, 10);
    const message = form.message?.value.trim() || '';
    const consentement = form.consentement?.checked;

    // =====================
    // B. Validation frontend
    // =====================
    if (!nom || !prenom || !telephone || !email || !date_souhaitee || isNaN(service)) {
      alert("❌ Veuillez remplir tous les champs obligatoires.");
      return;
    }

    if (!consentement) {
      alert("⚠️ Vous devez accepter le traitement de vos données.");
      return;
    }

    // =====================
    // C. Construction du payload
    // =====================
    const formData = {
      nom,
      prenom,
      telephone,
      email,
      date_souhaitee,
      service,
      message
      // statut est géré côté backend (par défaut à 'pending')
    };

    // =====================
    // D. Requête vers l'API Django
    // =====================
    try {
      const csrftoken = getCookie('csrftoken');
      console.log("[📤 Données envoyées]", formData);
      const response = await fetch('http://127.0.0.1:8000/prendre-rendez-vous/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(formData)
      });
let result = {};
try {
  result = await response.json();
  console.log("[🟡 RESULTAT BACKEND]", result); // AJOUTE CECI
} catch (e) {
  console.warn("Réponse vide ou non-JSON");
}

if (result.status === 'ok') {
    alert("✅ Rendez-vous enregistré avec succès !");
    form.reset();
} else {
    console.warn("[🟡 RESULTAT BACKEND]", result);
    
    // Affiche les erreurs de manière lisible
    const errors = result.errors || {};
    let messages = Object.entries(errors).map(([field, errs]) => {
        return `${field} : ${errs.join(', ')}`;
    }).join('\n');

    alert(`❌ Erreur: ${result.message}\n\n${messages}`);
}

      // =====================
      // E. Gestion des réponses
      // =====================
      if (response.ok) {
        alert("✅ Rendez-vous enregistré avec succès !");
        form.reset();
      } else {
        const message = result?.message || result?.detail || Object.values(result)?.[0] || 'Une erreur est survenue.';
        alert(`❌ Erreur: ${message}`);
      }
    } catch (err) {
      console.error('[ERREUR]', err);
      alert("❌ Erreur de connexion au serveur. Veuillez réessayer.");
    }
  });
});
