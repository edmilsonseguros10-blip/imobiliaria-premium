import { useState, useMemo } from 'react';
import { Header } from '@/components/Header';
import { Hero } from '@/components/Hero';
import { PropertyGrid } from '@/components/PropertyGrid';
import { PropertyFormModal } from '@/components/PropertyFormModal';
import { Footer } from '@/components/Footer';
import { mockProperties, Property } from '@/data/properties';

const Index = () => {
  const [cadastroOpen, setCadastroOpen] = useState(false);
  const [properties, setProperties] = useState<Property[]>(mockProperties);
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    tipoNegocio: '',
  });

  const filteredProperties = useMemo(() => {
    return properties.filter((property) => {
      const matchesSearch =
        !filters.search ||
        property.title.toLowerCase().includes(filters.search.toLowerCase()) ||
        property.description.toLowerCase().includes(filters.search.toLowerCase()) ||
        property.endereco?.toLowerCase().includes(filters.search.toLowerCase());

      const matchesCategory =
        !filters.category ||
        filters.category === 'all' ||
        property.category === filters.category;

      const matchesTipoNegocio =
        !filters.tipoNegocio ||
        filters.tipoNegocio === 'all' ||
        property.tipoNegocio === filters.tipoNegocio;

      return matchesSearch && matchesCategory && matchesTipoNegocio;
    });
  }, [properties, filters]);

  const handleSearch = (newFilters: typeof filters) => {
    setFilters(newFilters);
  };

  const handleAddProperty = (property: Omit<Property, 'id'>) => {
    const newProperty: Property = {
      ...property,
      id: Date.now().toString(),
    };
    setProperties((prev) => [newProperty, ...prev]);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header onOpenCadastro={() => setCadastroOpen(true)} />
      
      <main className="flex-1">
        <Hero onSearch={handleSearch} />
        <PropertyGrid properties={filteredProperties} />
      </main>

      <Footer />

      <PropertyFormModal
        open={cadastroOpen}
        onOpenChange={setCadastroOpen}
        onSubmit={handleAddProperty}
      />
    </div>
  );
};

export default Index;



