import React, { useState } from 'react';
import { View, TextInput, Button, FlatList, Text, Alert } from 'react-native';

export default function SearchComponent() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [status, setStatus] = useState('Idle');

  const runSearch = async () => {
    if (!query.trim()) {
      Alert.alert("Enter a search query first");
      return;
    }

    setStatus('Searching...');
    try {
      const res = await fetch("192.168.1.248:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          start_person: "Sid Nirgudkar",  // 🔁 Replace with current user’s contact name
          query_text: query
        })
      });

      const data = await res.json();
      if (data.results?.length > 0) {
        setResults(data.results);
        setStatus(`Found ${data.results.length} results`);
      } else {
        setResults([]);
        setStatus("No results found");
      }
    } catch (err) {
      console.error(err);
      Alert.alert("Failed to query backend");
      setStatus("Error");
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <TextInput
        placeholder="What do you need help with?"
        value={query}
        onChangeText={setQuery}
        style={{ borderWidth: 1, padding: 8, marginBottom: 10 }}
      />
      <Button title="Search Contacts" onPress={runSearch} />
      <Text style={{ marginVertical: 10 }}>{status}</Text>
      <FlatList
        data={results}
        keyExtractor={(_, index) => index.toString()}
        renderItem={({ item }) => (
          <View style={{ marginVertical: 5 }}>
            <Text style={{ fontWeight: 'bold' }}>{item[0]}</Text>
            <Text>Score: {item[1]} | Cost: {item[2]} | Domain Match: {item[3]}</Text>
            <Text>Path: {item[4]?.join(" → ")}</Text>
          </View>
        )}
      />
    </View>
  );
}
