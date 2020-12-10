// Changes from core:
// 1. form title is change from h2 to strong
// 2. new_password_help_text is changed
// 3. replaced and updated label with placeholder for password1
// 4. replaced label with placeholder for confirm password
// 5. Added div text-center outside button
// 6. Added 'button' class for <button>
// 7. Updated primaryActionButtonLabel
// 8. updated formTitle
// 9. updated PasswordResetInput import.
// 10. Added field types passwordType1 and passwordType2 in state.
// 11. Added two functions onClickPassword1 and onClickPassword2.
// 12. Added type and onClickHandler in props to PasswordResetInput fields.

/* globals gettext */

import 'whatwg-fetch';
import PropTypes from 'prop-types';
import React from 'react';

import { Button, StatusAlert } from '@edx/paragon/static';

import PasswordResetInput from './PasswordResetInput';

// NOTE: Use static paragon with this because some internal classes (StatusAlert at least)
// conflict with some standard LMS ones ('alert' at least). This means that you need to do
// something like the following on any templates that use this class:
//
// <link type='text/css' rel='stylesheet' href='${STATIC_URL}paragon/static/paragon.min.css'>
//

class PasswordResetConfirmation extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      password: '',
      passwordConfirmation: '',
      showMatchError: false,
      isValid: true,
      validationMessage: '',
      passwordType1: 'password',
      passwordType2: 'password',
    };
    this.onBlurPassword1 = this.onBlurPassword1.bind(this);
    this.onBlurPassword2 = this.onBlurPassword2.bind(this);
    this.onClickPassword1 = this.onClickPassword1.bind(this);
    this.onClickPassword2 = this.onClickPassword2.bind(this);
  }

  onClickPassword1() {
      this.setState({
          passwordType1: this.state.passwordType1 === 'password' ? 'text' : 'password'
      });
  }

  onClickPassword2() {
      this.setState({
          passwordType2: this.state.passwordType2 === 'password' ? 'text' : 'password'
      });
  }

  onBlurPassword1(password) {
    this.updatePasswordState(password, this.state.passwordConfirmation);
    this.validatePassword(password);
  }

  onBlurPassword2(passwordConfirmation) {
    this.updatePasswordState(this.state.password, passwordConfirmation);
  }

  updatePasswordState(password, passwordConfirmation) {
    this.setState({
      password,
      passwordConfirmation,
      showMatchError: !!password && !!passwordConfirmation && (password !== passwordConfirmation),
    });
  }

  validatePassword(password) {
    fetch('/api/user/v1/validation/registration', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        password,
      }),
    })
    .then(res => res.json())
    .then((response) => {
      let validationMessage = '';
      // Be careful about grabbing this message, since we could have received an HTTP error or the
      // endpoint didn't give us what we expect. We only care if we get a clear error message.
      if (response.validation_decisions && response.validation_decisions.password) {
        validationMessage = response.validation_decisions.password;
      }
      this.setState({
        isValid: !validationMessage,
        validationMessage,
      });
    });
  }

  render() {
    return (
      <section id="password-reset-confirm-anchor" className="form-type">
        <div id="password-reset-confirm-form" className="form-wrapper" aria-live="polite">
          <StatusAlert
            alertType="danger"
            dismissible={false}
            open={!!this.props.errorMessage}
            dialog={this.props.errorMessage}
          />

          <form id="passwordreset-form" method="post" action="">
            <strong className="from-h-style">
              <span className="text">
                {this.props.formTitle}
              </span>
            </strong>

            <h3 className="" id="new_password_help_text">
              {gettext('Please enter a new password below.' +
                  ' Passwords must be at least 8 characters and contain at least 1 number and 1 uppercase letter.')}
            </h3>

            <PasswordResetInput
              name="new_password1"
              describedBy="new_password_help_text"
              placeholder={gettext('Password')}
              onBlur={this.onBlurPassword1}
              isValid={this.state.isValid}
              validationMessage={this.state.validationMessage}
              type={this.state.passwordType1}
              onClickHandler={this.onClickPassword1}
            />

            <PasswordResetInput
              name="new_password2"
              describedBy="new_password_help_text"
              placeholder={gettext('Confirm Password')}
              onBlur={this.onBlurPassword2}
              isValid={!this.state.showMatchError}
              validationMessage={gettext('Passwords do not match.')}
              type={this.state.passwordType2}
              onClickHandler={this.onClickPassword2}
            />

            <input
              type="hidden"
              id="csrf_token"
              name="csrfmiddlewaretoken"
              value={this.props.csrfToken}
            />

            <div className="text-center">
                <Button
                    type="submit"
                    className={['action', 'action-primary', 'action-update', 'js-reset', 'button']}
                    label={this.props.primaryActionButtonLabel}
                />
            </div>
          </form>
        </div>
      </section>
    );
  }
}

PasswordResetConfirmation.propTypes = {
  csrfToken: PropTypes.string.isRequired,
  errorMessage: PropTypes.string,
  primaryActionButtonLabel: PropTypes.string,
  formTitle: PropTypes.string,
};

PasswordResetConfirmation.defaultProps = {
  errorMessage: '',
  primaryActionButtonLabel: gettext('CHANGE PASSWORD'),
   formTitle: gettext('Password Reset'),
};

export { PasswordResetConfirmation }; // eslint-disable-line import/prefer-default-export
