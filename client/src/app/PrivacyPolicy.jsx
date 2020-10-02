import React from 'react';

export default function PrivacyPolicy({ company, dataCenter, informationCommissioner }) {
  return (
    <div className="privacy-policy">
      <h2>Musical Bingo Privacy Policy</h2>
      <p>This privacy policy will explain how our organization ({company.name}) uses the
        personal data we collect from you when you use our website.
        </p>

      <p>Topics:</p>
      <ul>
        <li>What data do we collect?</li>
        <li>How do we collect your data?</li>
        <li>How will we use your data?</li>
        <li>How do we store your data?</li>
        <li>Marketing</li>
        <li>What are your data protection rights?</li>
        <li>What are cookies?</li>
        <li>How do we use cookies?</li>
        <li>What types of cookies do we use?</li>
        <li>How to manage your cookies</li>
        <li>Privacy policies of other websites</li>
        <li>Changes to our privacy policy</li>
        <li>How to contact us</li>
        <li>How to contact the appropriate authorities</li>
      </ul>
      <h3>What data do we collect?</h3>
      <p>Our Company collects the following data:</p>
      <ul>
        <li>Email address</li>
        <li>Username</li>
        <li>Date and time when application is used</li>
      </ul>
      <h3>How do we collect your data?</h3>
      <p>
        You directly provide Our Company with most of the data we collect.
        We collect data and process data when you:
        </p>
      <ul>
        <li>Register online.</li>
        <li>Use or view our website via your browser's cookies and authentication tokens.</li>
      </ul>
      <h3>How will we use your data?</h3>
      <p>
        Our Company collects your data so that we can:
        </p>
      <ul>
        <li>Manage your account.</li>
        <li>Email you with details on how to reset your password, when
          requested by you</li>
      </ul>
      <p>
        Our Company will not share your data with other companies.
      </p>
      <h3>How do we store your data?</h3>
      <p>
        Our Company securely stores your data {dataCenter}.
      </p>
      <p>
        The password is stored in a form that does not allow the value of the
        password to be easily retrieved. We are unable to tell you what your
        password is, but we can assist you in changing the password. We will never
        send your password in an email.
      </p>
      <p>
        Our Company will keep your account details until you request their removal.
      </p>
      <h3>Marketing</h3>
      <p>
        Our Company will <em>never</em> send you information about other products
        or services.
        </p>
      <h3>What are your data protection rights?</h3>
      <p>
        Our Company would like to make sure you are fully aware of all of your data
        protection rights. Every user is entitled to the following:
      </p>
      <ul>
        <li>
          The right to access - You have the right to request Our Company for copies of your
          personal data. We may charge you a small fee for this service.
          </li>
        <li>
          The right to rectification - You have the right to request that Our Company
          correct any information you believe is inaccurate. You also have the right to request
          Our Company to complete the information you believe is incomplete.
          </li>
        <li>
          The right to erasure - You have the right to request that Our Company erase your
          personal data, under certain conditions.
          </li>
        <li>
          The right to restrict processing - You have the right to request that Our Company
          restrict the processing of your personal data, under certain conditions.
          </li>
        <li>
          The right to object to processing - You have the right to object to Our Company's
          processing of your personal data, under certain conditions.
          </li>
        <li>
          The right to data portability - You have the right to request that Our Company transfer
          the data that we have collected to another organization, or directly to you, under
          certain conditions.
          </li>
      </ul>
      <p>
        If you make a request, we have one month to respond to you. If you would like to exercise
        any of these rights, please contact us at our
        email: <a href={`mailto:${company.email}`}>{company.email}</a>
      </p>
      <h3>Cookies and Authentication Tokens</h3>
      <p>
        Cookies and authentication tokens are text files placed into your computer's browser to allow it to access
        this website, to collect standard Internet log information and visitor behaviour information.
        When you visit this website, we may collect
        information from you automatically through cookies or authentication tokens.
      </p>
      <p>For further information, visit <a href="https://allaboutcookies.org">allaboutcookies.org</a>.</p>
      <h3>How do we use cookies and authentication tokens?</h3>
      <p>
        Our Company uses cookies and authentication tokens in a range of ways to improve your experience on this
        website, including:
      </p>
      <ul>
        <li>Keeping you signed in</li>
        <li>Understanding how you use our website</li>
      </ul>
      <h3>What types of cookies do we use?</h3>
      <p>There are a number of different types of cookies, however, our website uses:</p>
      <ul>
        <li>Functionality - Our Company uses these cookies so that we recognize you on
        our website and remember your previously selected preferences. These could include what
        language you prefer and location you are in. Only first-party cookies are used.</li>
      </ul>
      <h3>How to manage cookies</h3>
      <p>
        You can set your browser not to accept cookies, and the above website tells you how to remove
        cookies from your browser. However, in a few cases, some of our website features might not function
        as a result.
      </p>
      <h3>What types of authentication tokens do we use?</h3>
      <p>
        When using any features of this website that requires you to have logged in, an authentication token
        is sent in each request from your browser to the website. This token is used to relate these
        requests to your user account.
      </p>
      <p>
        There are two types of authentication tokens used by this website:
      </p>
      <ul>
        <li>Access token - a token that allows access to features of the website, but is only valid for a few minutes
        </li>
        <li>Refresh token - a token that is used to request a new access token. The refresh token has a
          lifetime of one or more days. It is used to save you from having to log in every
          time the access token expires. If the "remember me" tick box has been selected when logging
          into the website, the refresh token is given a longer lifetime than if the tick box is not
          selected.
        </li>
      </ul>
      <h3>How to manage authentication tokens</h3>
      <p>
        Access tokens are lost when the webpage is reloaded, or when they expire. You can remove the current
        access token by logging out of the website and reloading the page (for example using Ctrl+F5).
        Refresh tokens are stored in an area of your browser called "local storage". You can use a
        search engine to search for "clear local storage" to find a step-by-step guide to removing the
        refresh token from local storage on your browser.
      </p>
      <h3>Privacy policies of other websites</h3>
      <p>
        This website contains links to other websites. Our privacy policy applies only to our website,
        so if you click on a link to another website, you should read their privacy policy.
      </p>
      <h3>Changes to our privacy policy</h3>
      <p>
        Our Company keeps its privacy policy under regular review and places any updates on this web
        page. This privacy policy was last updated on 2 October 2020.
      </p>
      <h3>How to contact us</h3>
      <p>
        If you have any questions about Our Company's privacy policy, the data we hold on you, or you
        would like to exercise one of your data protection rights, please do not hesitate to contact us.
        </p>
      <p>Email us at: <a href={`mailto:${company.email}`}>{company.email}</a></p>
      {company.address && <p>Or write to us at: {company.address}</p>}
      <h3>How to contact the appropriate authority</h3>
      <p>
        Should you wish to report a complaint or if you feel that Our Company has not addressed your
        concern in a satisfactory manner, you may contact the Information Commissioner's Office.
        </p>
      <p>Address: <a href={informationCommissioner.link}>{informationCommissioner.text}</a> </p>
    </div>
  );
}
