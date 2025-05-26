import React, { useState, useEffect } from 'react';
import { Button, View, Text, Alert } from 'react-native';
import * as AuthSession from 'expo-auth-session';
import * as WebBrowser from 'expo-web-browser';

WebBrowser.maybeCompleteAuthSession();

const CLIENT_ID = 'YOUR_GOOGLE_CLIENT_ID'; // 🔑 replace this
const REDIRECT_URI = AuthSession.makeRedirectUri({ useProxy: true });

const DISCOVERY = {
  authorizationEndpoint: 'https://accounts.google.com/o/oauth2/v2/auth',
  tokenEndpoint: 'https://oauth2.googleapis.com/token',
};

export default function GmailOAuth({ onEmailsReady }) {
  const [token, setToken] = useState(null);
  const [status, setStatus] = useState('Idle');

  const [request, response, promptAsync] = AuthSession.useAuthRequest(
    {
      clientId: CLIENT_ID,
      scopes: ['https://www.googleapis.com/auth/gmail.readonly'],
      redirectUri: REDIRECT_URI,
      responseType: 'token',
    },
    DISCOVERY
  );

  useEffect(() => {
    if (response?.type === 'success') {
      const { access_token } = response.params;
      setToken(access_token);
      setStatus('Authenticated');
    }
  }, [response]);

  const fetchEmailContacts = async () => {
    if (!token) {
      Alert.alert('Token not ready. Please authorize first.');
      return;
    }

    setStatus('Fetching Gmail metadata...');

    try {
      const res = await fetch('https://www.googleapis.com/gmail/v1/users/me/messages?maxResults=25', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const json = await res.json();

      const emails = json.messages || [];
      const enriched = emails.map(e => ({
        name: null,
        email: e.id + "@gmail.fake", // Placeholder, Gmail API doesn't expose actual contact email directly without message read
        phone: null,
        profession: null,
        tags: ['gmail'],
        source: 'gmail',
        communication_count: 1,
        last_contacted: new Date().toISOString()
      }));

      setStatus(`Pulled ${enriched.length} Gmail entries`);
      onEmailsReady(enriched); // ⬅️ pass to parent

    } catch (err) {
      console.error(err);
      Alert.alert('Failed to fetch Gmail metadata');
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <Button disabled={!request} title="Connect Gmail" onPress={() => promptAsync()} />
      {token && <Button title="Fetch Gmail Metadata" onPress={fetchEmailContacts} />}
      <Text style={{ marginTop: 10 }}>{status}</Text>
    </View>
  );
}
