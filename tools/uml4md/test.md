# Test file for updatemd.py

Some introductory text.

## Sequence diagram

![](.img/077301032c23b097c6c61e5518fc5298.png)

<details>
<summary>View UML</summary>

```uml
Alice -> Bob : hello
Bob --> Alice : hi there
```

</details>

## Class diagram

![](.img/dc5ba55beb1d8c7342a936047bea87ea.png)

<details>
<summary>View UML</summary>

```uml
class Animal {
  +name : string
  +speak() : void
}

class Dog {
  +fetch() : void
}

Animal <|-- Dog
```

</details>

## Flow diagram / Activity diagram

```uml
start
:Process starts;
if (Condition met?) then (yes)
  :Execute task A;
  :Execute task B;
else (no)
  :Skip tasks;
endif
:Process ends;
stop
```

## End

That's all.
