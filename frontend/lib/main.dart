import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const PeerTutoringApp());
}

class PeerTutoringApp extends StatelessWidget {
  const PeerTutoringApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Peer Tutoring Platform',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: Colors.indigo,
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
