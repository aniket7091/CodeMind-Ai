function ErrorMessage({ message }) {
  if (!message) {
    return null;
  }

  return (
    <div className="error-message">
      <div className="error-icon">!</div>

      <div>
        <strong>Something went wrong</strong>
        <p>{message}</p>
      </div>
    </div>
  );
}

export default ErrorMessage;