const labels = ['name', 'email', 'phone', 'message']

const submitBtn = document.querySelector('input[type="submit"]') 
const popUp = document.getElementsByClassName('pop-up')[0]
const errorMessage = document.getElementById('errorMessage')
const info = {}

const emailPattern = /^[\w-\.]+@([\w-]+\.)+[\w-]/

var isNameEmpty = true
var isEmailinValid = true
var isMessageEmpty = true

const validation = (key, value) => {
    if (key == 'name') {
        isNameEmpty = value.trim() === ''
    } else if (key == 'email') {
        isEmailinValid = !emailPattern.test(value)
    } else if (key == 'phone') {

    } else {
        isMessageEmpty = value.trim() === ''
    }
    if (isNameEmpty || isEmailinValid || isMessageEmpty) {
        submitBtn.disabled = true;
    } else {
        submitBtn.disabled = false;
        errorMessage.style.display = 'none';
    }
    if (isNameEmpty) {
        errorMessage.style.display = 'block';
        errorMessage.textContent = 'Name is required.';
    } else if (isEmailinValid) {
        errorMessage.style.display = 'block';
        errorMessage.textContent = 'invalid email or you have not enter an email.';
    } else if (isMessageEmpty) {
        errorMessage.style.display = 'block';
        errorMessage.textContent = 'Message is required.';
    }
}

labels.forEach(key => {
    const dom = document.getElementsByName(key)[0]
    dom.addEventListener('input', () => {
        info[key] = dom.value
        validation(key, dom.value)
    })
})

submitBtn.addEventListener('click', () => {
    let formData = new FormData()
    Object.keys(info).forEach(key => {
        document.getElementsByName(key)[0].setAttribute('disabled', true)
        formData.append(key, info[key])
    });
    formData.append('time', new Date())
    submitBtn.setAttribute('disabled', true)
    submitBtn.value = 'SENDING...'
    fetch(
        '/api/contact_form',
        {
            method: 'POST',
            body: formData,
            redirect: "follow",
        } 
    ).then(res => res.json()).then(async (d) => {
        if (d.status == "success") {
            labels.forEach(key => {
                info[key] = ''
                document.getElementsByName(key)[0].value = ''
                document.getElementsByName(key)[0].removeAttribute('disabled')
            })
            submitBtn.removeAttribute('disabled')
            submitBtn.value = 'SUBMIT'
            popUp.style.opacity = 1
            setTimeout(() => popUp.style.opacity = 0, 2250)
        } else {
            console.log(d.message)
            popUp.style.opacity = 1
            popUp.textContent = 'Failed to submit'
            setTimeout(() => {
                popUp.style.opacity = 0
                popUp.textContent = 'Submission Completed'
            }, 2250)
            submitBtn.removeAttribute('disabled')
            submitBtn.value = 'SUBMIT'  
        }
    }).catch((e) => {
        console.log(e)
        submitBtn.removeAttribute('disabled')
        submitBtn.value = 'SUBMIT'  
    })
})