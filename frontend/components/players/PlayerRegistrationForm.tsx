import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { createPlayer } from "@/services/playerService";
import { Loader2 } from "lucide-react";

const formSchema = z.object({
  name: z.string().min(2, {
    message: "Le nom doit contenir au moins 2 caractères.",
  }),
});

interface PlayerRegistrationFormProps {
  onPlayerRegistered: () => void;
}

export function PlayerRegistrationForm({
  onPlayerRegistered,
}: PlayerRegistrationFormProps) {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      await createPlayer(values.name);
      toast.success("Création du joueur effectuée", {
        description: `Création du joueur ${values.name} effectuée.`,
      });
      form.reset();
      onPlayerRegistered();
    } catch (error: any) {
      // Check for duplicate player name (409 Conflict status)
      if (error.response && error.response.status === 409) {
        toast.error("Nom de joueur déjà utilisé", {
          description:
            "Un joueur avec ce nom existe déjà. Veuillez choisir un nom différent.",
        });
        // Set form error
        form.setError("name", {
          type: "manual",
          message: "Ce nom est déjà utilisé par un autre joueur",
        });
      } else {
        toast.error("Création du joueur echouée", {
          description:
            error instanceof Error
              ? error.message
              : "Une erreur inconnue est survenue.",
        });
      }
      console.error("Création du joueur echouée:", error);
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 pt-2">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Nom du joueur</FormLabel>
              <FormControl>
                <Input placeholder="Nom du joueur" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button
          type="submit"
          className="w-full"
          disabled={form.formState.isSubmitting}
        >
          {form.formState.isSubmitting && (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          )}
          {form.formState.isSubmitting ? "Création..." : "Créer le joueur"}
        </Button>
      </form>
    </Form>
  );
}
