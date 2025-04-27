import { useEffect, useState } from 'react';
import { PlaidLink } from 'react-plaid-link';

export default function PlaidLinker() {
  const [linkToken, setLinkToken] = useState(null);

  useEffect(() => {
    async function createLinkToken() {
      const response = await fetch('/api/create_link_token', { method: 'POST' });
      const data = await response.json();
      setLinkToken(data.link_token);
    }

    createLinkToken();
  }, []);

  const onSuccess = async (public_token, metadata) => {
    console.log('Success! Public Token: ', public_token);

    await fetch('/api/exchange_public_token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ public_token }),
    });

  };

  if (!linkToken) {
    return <div></div>;
  }

  return (
    <PlaidLink
      token={linkToken}
      onSuccess={onSuccess}
      onExit={(err, metadata) => {
        if (err) {
          console.error('Plaid Link exited with error', err);
        }
      }}
    >
      Connect a bank account
    </PlaidLink>
  );
}
