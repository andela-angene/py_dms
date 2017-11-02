import React, { PropTypes } from 'react';
import { connect } from 'react-redux';
import { saveDocument } from '../../actions/documentActions';
import { validateSaveDocument } from '../../utilities/validator';
import DocumentForm from './DocumentForm';
import { handleError } from '../../utilities/errorHandler';

/**
 * Document form container
 *
 * @class ManageDocument
 * @extends {React.Component}
 */
class ManageDocument extends React.Component {
  constructor(props) {
    super(props);
    this.state = Object.assign({ errors: {} }, props.document);
    this.onSubmit = this.onSubmit.bind(this);
    this.onChange = this.onChange.bind(this);
    this.getContent = this.getContent.bind(this);
  }

  /**
  * Validate and submit the form
  *
  * @param {Object} event
   * @returns {Undefined} nothing
   */
  onSubmit(event) {
    event.preventDefault();
    const { valid, errors } = validateSaveDocument(this.state);
    if (valid) {
      this.setState({ errors: {} });
      this.props
        .saveDocument(this.state)
        .then(() => {
          this.context.router.push('/');
        })
        .catch(error => handleError(error));
    } else {
      this.setState({ errors });
    }
  }

  /**
  * Control input fields
  *
  * @param {Object} event
  * @returns {Undefined} nothing
  */
  onChange(event) {
    return this.setState({ [event.target.name]: event.target.value });
  }

  /**
  * Get the content of the Froala editor
  *
  * @param {String} text
  * @returns {Undefined} nothing
  */
  getContent(text) {
    this.setState({ content: text });
  }

  componentDidMount() {
    if ($('.fr-wrapper > div').length > 1) {
      $('.fr-wrapper').addClass('fr-wrapper-h');
    }
  }

  /**
  * Render the component
  *
  * @returns {Object} jsx component
   */
  render() {
    const accessOptions = [
      { value: 'public', text: 'Public' },
      { value: 'private', text: 'Private' },
      { value: 'role', text: 'Role' },
    ];
    const categories = this.props.categories.map(category => ({
      value: category.name,
      text: category.name,
    }));

    return (
      <DocumentForm
        onChange={this.onChange}
        document={this.state}
        onSubmit={this.onSubmit}
        getContent={this.getContent}
        accessOptions={accessOptions}
        categories={categories}
      />
    );
  }
}

ManageDocument.contextTypes = {
  router: PropTypes.object.isRequired,
};

/**
 * Filter and map the correct document to props
 *
 * @param {Object} state redux store state
 * @param {Object} ownProps own props
 * @returns {Object} document object
 */
function mapStateTopProps(state, ownProps) {
  let currentDocument = {
    title: '',
    content: '',
    access: 'null',
    category: 'null',
  };
  const documentId = ownProps.params.id;
  if (documentId) {
    state.documents.forEach((document) => {
      if (Number(documentId) === document.id) {
        currentDocument = {
          title: document.title,
          content: document.content,
          access: document.access,
          updateId: document.id,
          category: document.category ? document.category : 'null',
        };
      }
    });
  }

  return {
    document: currentDocument,
    categories: state.categories,
  };
}

ManageDocument.propTypes = {
  document: PropTypes.object.isRequired,
  categories: PropTypes.array.isRequired,
  saveDocument: PropTypes.func.isRequired,
};

export default connect(mapStateTopProps, { saveDocument })(ManageDocument);
