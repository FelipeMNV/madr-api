from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))


@table_registry.mapped_as_dataclass
class Romancista:
    __tablename__ = 'romancistas'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    livros: Mapped[list['Livro']] = relationship(
        back_populates='romancista',
        init=False,
    )


@table_registry.mapped_as_dataclass
class Livro:
    __tablename__ = 'livros'
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    ano: Mapped[int] = mapped_column(nullable=False)
    romancista_id: Mapped[int] = mapped_column(ForeignKey('romancistas.id'))

    romancista: Mapped['Romancista'] = relationship(
        back_populates='livros',
        init=False,
    )
