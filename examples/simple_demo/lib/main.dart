import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

void main() {
  _setTargetPlatformForDesktop();
  runApp(MyApp());
}

void _setTargetPlatformForDesktop() {
  TargetPlatform targetPlatform;
  if (Platform.isMacOS) {
    targetPlatform = TargetPlatform.iOS;
  } else if (Platform.isLinux || Platform.isWindows) {
    targetPlatform = TargetPlatform.android;
  }
  if (targetPlatform != null) {
    debugDefaultTargetPlatformOverride = targetPlatform;
  }
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return new MaterialApp(
      title: 'Flutter Demo',
      theme: new ThemeData(
        // If the host is missing some fonts, it can cause the
        // text to not be rendered or worse the app might crash.
        fontFamily: 'Roboto',
        primarySwatch: Colors.blue,
      ),
      home: new MyHomePage(title: 'python flutter desktop embedder'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  MyHomePage({Key key, this.title}) : super(key: key);

  final String title;

  @override
  _MyHomePageState createState() {
    return new _MyHomePageState();
  }
}

class _MyHomePageState extends State<MyHomePage> {
  static MethodChannel _channel =
      new MethodChannel('simple_demo_plugin', new JSONMethodCodec());
  int _counter = 0;
  var _theValue, _listValue, _dictValue, _poetry;
  FocusNode nextFocus = FocusNode();

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return new Scaffold(
      appBar: new AppBar(
        title: new Text(widget.title),
      ),
      body: new Center(
        child: new Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            new Text(
              'You have pushed the button this many times:',
              style: TextStyle(fontSize: 18.0),
            ),
            new Text(
              '$_counter',
              style: Theme.of(context).textTheme.display1,
            ),
            new Padding(
              padding: new EdgeInsets.all(8.0),
              child: new Column(children: <Widget>[
                TextField(
                  decoration: InputDecoration(
                      hintText:
                          'TextField【u can press the enter key to focus next textfield】'),
                  onSubmitted: (value) {
                    setState(() {});
                  },
                  onEditingComplete: () =>
                      FocusScope.of(context).requestFocus(nextFocus),
                ),
                TextField(
                  decoration: InputDecoration(
                      hintText:
                          'TextField【here press the enter key can make a new line】'),
                  maxLines: 2,
                  focusNode: nextFocus,
                  onSubmitted: (value) {
                    setState(() {});
                  },
                ),
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Text('Plugin methods'),
                ),
                Padding(
                  padding: const EdgeInsets.all(18.0),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      RaisedButton(
                        onPressed: () async {
                          var result =
                              await _channel.invokeMethod('getTheValue');
                          setState(() {
                            _theValue = result;
                          });
                        },
                        child: Text('button1'),
                      ),
                      Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: Text('the value:$_theValue'),
                      )
                    ],
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(18.0),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      RaisedButton(
                        onPressed: () async {
                          var result =
                              await _channel.invokeMethod('getListValue');
                          setState(() {
                            _listValue = result;
                          });
                        },
                        child: Text('button2'),
                      ),
                      Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: Text('list value:$_listValue'),
                      )
                    ],
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(18.0),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      RaisedButton(
                        onPressed: () async {
                          var result =
                              await _channel.invokeMethod('getDictValue');
                          setState(() {
                            _dictValue = result;
                          });
                        },
                        child: Text('button3'),
                      ),
                      Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: Text('dict value:$_dictValue'),
                      )
                    ],
                  ),
                ),
              ]),
            ),
          ],
        ),
      ),
      floatingActionButton: new FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: new Icon(Icons.add),
      ),
    );
  }
}
