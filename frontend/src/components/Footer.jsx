import '../styles/footer.css'
function Footer(){


    const date = new Date();
    return(
        <footer>
            <p className="thank-note">Thank You for visiting this website</p>
            <span className="ownership">&copy; {date.getFullYear()} All Rights Reserved</span>

        </footer>
    );
}

export default Footer