const deleteBtn = document.getElementById('delete-btn');
deleteBtn.addEventListener('click', async () => {
    const response = await fetch('/users/settings/delete_user', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            // Optional body payload
        })
    });

    if (response.ok) {
        setTimeout(() => {
            window.location.href = '/users/login';
          }, 2000);
    } else {
        // Handle error response
        console.error(`Error deleting account: ${response.statusText}`);
    }
});
