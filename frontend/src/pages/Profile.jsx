function Profile() {
  return (
    <div className="page">

      <span className="eyebrow">
        ACCOUNT
      </span>

      <h1>Your Profile</h1>

      <p className="page-description">
        Your profile is used by our AI
        to find better opportunities.
      </p>

      <div className="profile-card">

        <div className="profile-avatar big">
          A
        </div>

        <div>

          <h2>
            Aqdar Ahmad
          </h2>

          <p>
            Computer Systems Engineer
          </p>

        </div>

      </div>


      <div className="profile-section">

        <h2>Skills</h2>

        <div className="skills">

          <span>SystemVerilog</span>
          <span>UVM</span>
          <span>C++</span>
          <span>Python</span>
          <span>Design Verification</span>

        </div>

      </div>

    </div>
  );
}

export default Profile;