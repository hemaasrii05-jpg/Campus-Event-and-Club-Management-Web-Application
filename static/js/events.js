document.addEventListener('click', async function(e){
	if (e.target && e.target.classList.contains('rsvp-button')){
		const parent = e.target.closest('.event-item')
		const id = parent.dataset.id
		try{
			const res = await fetch(`/events/${id}/rsvp`, {method: 'POST'});
			const data = await res.json();
			if (res.ok) {
				alert(data.status || 'ok')
				location.reload()
			} else alert(data.error || 'error')
		}catch(err){
			alert('Network error')
		}
	}

	if (e.target && e.target.classList.contains('cancel-button')){
		const id = e.target.dataset.id
		try{
			const res = await fetch(`/events/${id}/cancel`, {method: 'POST'});
			const data = await res.json();
			if (res.ok) {
				alert(data.status || 'ok')
				location.reload()
			} else alert(data.error || 'error')
		}catch(err){
			alert('Network error')
		}
	}
})
