import fetchData from './fetch-data.js'

const labels = ['name', 'email', 'password']

const submitBtn = document.querySelector('button[type="submit"]') 
const popUp = document.getElementsByClassName('pop-up')[0]
const errorMessage = document.getElementById('errorMessage')
const info = {}

const emailPattern = /^[\w-\.]+@([\w-]+\.)+[\w-]/

var isNameEmpty = true
var isEmailInvalid = true
var isPasswordEmpty = true

const validation = (key, value) => {
    if (key == 'name') {
        isNameEmpty = value.trim() === ''
    } else if (key == 'email') {
        isEmailInvalid = !emailPattern.test(value)
    } else {
        isPasswordEmpty = value.trim() === ''
    }
    if (isNameEmpty || isEmailInvalid || isPasswordEmpty) {
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
    } else if (isPasswordEmpty) {
        errorMessage.style.display = 'block';
        errorMessage.textContent = 'Password is required.';
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
    submitBtn.setAttribute('disabled', true)
    submitBtn.textContent = 'loading...'
    const res = await fetchData('/api/account', formData)

    if (res.status == "success") {

        // set login data to sessionStorage
        sessionStorage.setItem('name', info.name);
        sessionStorage.setItem('email', info.email);
        
        popUp.style.opacity = 1

        popUp.textContent = res.message

        setTimeout(() => {
            popUp.style.opacity = 0;
            window.location.href = "/"; // back to Homepage
        }, 1500);

    } else if (res.status == "login") {
        sessionStorage.setItem('name', info.name);
        sessionStorage.setItem('email', info.email);

        popUp.style.opacity = 1

        popUp.textContent = res.message

        setTimeout(() => {
            popUp.style.opacity = 0;
            window.location.href = "/"; // back to Homepage
        }, 1500);
    } else {
        submitBtn.removeAttribute('disabled')
        const errorMesg = (Boolean(!res.message.isValidName) ? 'error name' + (Boolean(!res.message.isValidName) && Boolean(!res.message.isValidPassword)) ? ', ' : '' : '') + (Boolean(!res.message.isValidPassword) ? 'error password' : '')
        errorMessage.style.display = 'block';
        errorMessage.textContent = errorMesg
        labels.forEach(key => {
            document.getElementsByName(key)[0].removeAttribute('disabled')
        })
        submitBtn.textContent = 'Login / Sign up'
    }
})