let head = document.querySelector('header')

const navs = [
    { label: 'Price', href: '/price' },
    { label: 'Rent & Retrun', href: '/use' },
    { label: 'Contact us', href: '/contact' },
]

head.innerHTML = `
    <nav>
        <div class="flex divided">
            <a href="/">
                <div class="logo"><img width="100%" src="../static/images/logo.svg" /></div>
            </a>
            <div class="flex desktop">
                ${navs.map(({ label, href }) => (
                    `<div style="font-size: 1.75em; font-weight: bold; color: #002C3E"><a href=${href}>${label}</a></div>`
                )).join('')}
            </div>
        </div>
    </nav>
`

{/* <div class="mobile menu">
<img style="width: 40px" src="images/menu.png" />
<div class="dropdown-content">
    <li>
        <a href="about.html">
            ABOUT
        </a>
    </li>
    <li>
        <a href="portfolio.html">
            PORTFOLIO
        </a>
    </li>
    <li>
         <a href="gallery.html">
            GALLERY
        </a>
    </li>
    <li>
        <a href="contact.html">
            CONTACT
        </a>
    </li>
</div>
</div> */}