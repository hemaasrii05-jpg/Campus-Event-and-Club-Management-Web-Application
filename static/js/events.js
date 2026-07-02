document.addEventListener('click', async function(e){
	if (e.target && e.target.classList.contains('rsvp-button')){
		const parent = e.target.closest('.event-item')
		const id = parent.dataset.id
		try{
			const res = await fetch(`/events/${id}/rsvp`, {method: 'POST'});
			const data = await res.json();
			if (res.ok) {
				window.ui && window.ui.showToast && window.ui.showToast(data.status || 'Registered', 'success')
				setTimeout(()=>location.reload(), 900)
			} else alert(data.error || 'error')
		}catch(err){
			window.ui && window.ui.showToast && window.ui.showToast('Network error', 'error')
		}
	}

	if (e.target && e.target.classList.contains('cancel-button')){
		const id = e.target.dataset.id
		if (window.ui && window.ui.showConfirm) {
			const ok = await window.ui.showConfirm('Are you sure you want to unregister from this event?')
			if (!ok) return
		}
		try{
			const res = await fetch(`/events/${id}/cancel`, {method: 'POST'});
			const data = await res.json();
			if (res.ok) {
				window.ui && window.ui.showToast && window.ui.showToast(data.status || 'Cancelled', 'success')
				setTimeout(()=>location.reload(), 900)
			} else window.ui && window.ui.showToast && window.ui.showToast(data.error || 'Error', 'error')
		}catch(err){
			window.ui && window.ui.showToast && window.ui.showToast('Network error', 'error')
		}
	}
})
