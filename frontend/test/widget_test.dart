import 'package:flutter_test/flutter_test.dart';
import 'package:peer_tutoring_app/main.dart';

void main() {
  testWidgets('home screen shows the main peer tutoring actions', (WidgetTester tester) async {
    await tester.pumpWidget(const PeerTutoringApp());

    expect(find.text('AI-Based Peer Tutoring\nMatching Platform'), findsOneWidget);
    expect(find.text("I'm a Learner"), findsOneWidget);
    expect(find.text("I'm a Tutor"), findsOneWidget);
    expect(find.text('Learning Materials'), findsOneWidget);
    expect(find.text('Manage Sessions'), findsOneWidget);
  });
}
