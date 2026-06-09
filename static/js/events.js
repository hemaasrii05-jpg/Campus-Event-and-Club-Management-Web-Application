document.addEventListener('click', async function(e){
	if (e.target && e.target.classList.contains('rsvp-button')){
		const parent = e.target.closest('.event-item')
		const id = parent.dataset.id
		try{
			const res = await fetch(`/events/${id}/rsvp`, {method: 'POST'});
			const data = await res.json();
			if (res.ok) alert(data.status || 'ok')
			else alert(data.error || 'error')
		}catch(err){
			alert('Network error')
		}
	}
})
