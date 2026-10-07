import { Link } from 'react-router-dom'

export default function About() {
  return (
    <article className="prose">
      <h1>About Us</h1>
      <p>
        Campus Customs started with a simple idea: Yale pride should be something you can wear every day, not just on
        game day. We design comfortable, well-made apparel that celebrates the people, places, and traditions that make
        Yale feel like home.
      </p>

      <h2>Who we make it for</h2>
      <p>
        Our gear is for the whole Yale community. That means students heading to class on Old Campus, alumni coming back
        for reunion, parents and grandparents cheering from the stands, and fans who just love the Bulldogs.
      </p>

      <h2>What you'll find</h2>
      <ul>
        <li>Everyday tees, crewnecks, and hoodies with classic Yale marks.</li>
        <li>Pieces for the residential colleges, from Berkeley to Davenport.</li>
        <li>Team designs for varsity sports, plus gear for The Game against Harvard.</li>
        <li>Quarter-zips, fleece, and jackets for New Haven winters.</li>
      </ul>

      <h2>How we work</h2>
      <p>
        We keep our collection focused and our stock honest. Every product page shows the sizes we actually have on the
        shelf, and our chat assistant uses the same live inventory to answer your questions.
      </p>

      <p>
        <Link to="/products" className="button">
          Browse the collection
        </Link>
      </p>
    </article>
  )
}
