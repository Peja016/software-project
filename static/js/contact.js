import fetchData from './fetchData.js'

const labels = ['name', 'email', 'phone', 'message']

const submitBtn = document.querySelector('input[type="submit"]') 
const popUp = document.getElementsByClassName('pop-up')[0]
const errorMessage = document.getElementById('errorMessage')
const info = {}

const emailPattern = /^[\w-\.]+@([\w-]+\.)+[\w-]/
const phonePattern = /^(?:\+?\d{1,4})?[ -.]?(?:\(?\d{2,4}\)?)[ -.]?\d{3,4}[ -.]?\d{3,4}$/

var isNameEmpty = true
var isEmailInvalid = true
var isMessageEmpty = true
var isPhoneInvalid = false

const validation = (key, value) => {
    if (key == 'name') {
        isNameEmpty = value.trim() === ''
    } else if (key == 'email') {
        isEmailInvalid = !emailPattern.test(value)
    } else if (key == 'phone') {
        if (Boolean(value)) {
            isPhoneInvalid = !phonePattern.test(value)
        } else {
            isPhoneInvalid = false
        }
    } else {
        isMessageEmpty = value.trim() === ''
    }
    if (isNameEmpty || isEmailInvalid || isMessageEmpty || isPhoneInvalid) {
        submitBtn.disabled = true;
    } else {
        submitBtn.disabled = false;
        errorMessage.style.display = 'none';
    }
    if (isNameEmpty) {
        errorMessage.style.display = 'block';
        errorMessage.textContent = 'Name is required.';
    } else if (isEmailInvalid) {
        errorMessage.style.display = 'block';
        errorMessage.textContent = 'Invalid email or you have not enter an email.';
    } else if (isPhoneInvalid) {
        errorMessage.style.display = 'block';
        errorMessage.textContent = 'Invalid phone number.';
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

submitBtn.addEventListener('click', async () => {
    let formData = new FormData()
    Object.keys(info).forEach(key => {
        document.getElementsByName(key)[0].setAttribute('disabled', true)
        formData.append(key, info[key])
    });
    formData.append('time', new Date())
    submitBtn.setAttribute('disabled', true)
    submitBtn.value = 'SENDING...'
    const d = await fetchData('/api/contact_form', formData)
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
        popUp.style.opacity = 1
        popUp.textContent = 'Failed to submit'
        setTimeout(() => {
            popUp.style.opacity = 0
            popUp.textContent = 'Submission Completed'
        }, 2250)
        submitBtn.removeAttribute('disabled')
        submitBtn.value = 'SUBMIT'  
    }

})