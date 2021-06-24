const hamburger = document.getElementsByClassName('hamburger')[0]
const nav = document.getElementsByClassName('nav')[0]

hamburger.addEventListener('click', () => {
  nav.classList.toggle('active')
})